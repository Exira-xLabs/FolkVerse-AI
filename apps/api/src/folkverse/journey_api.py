"""Owned journey routes: explicit preferences in, deterministic published stops out.

Every read re-resolves stored stops against the current published corpus. A withdrawn, deleted,
locale-unavailable or no-longer-fitting stop is pruned from the response and reported through an
explicit localized ``notice``; a stale title, duration or source URL is never displayed.
Selection preferences are only ever written by the visitor's own POST/PATCH, and every row is
owned by the signed session cookie rather than by request input.

Pruning is a read-time projection, deliberately not persisted: GET stays read-only so it cannot
race with a concurrent PATCH, and the response states exactly what was hidden. A stop that is
re-published later can therefore reappear, which is the documented tradeoff of that choice.

Selection is gated on real, approved ``https`` source links: a published exhibit with no usable
source is not selectable, so no stop can appear without a source the visitor can inspect.

The optional explanation step runs *after* the deterministic route is stored, on the request
event loop (the explainer shares one event loop for its single-flight cache). It may only pick
reason codes from the frozen vocabulary of ``folkverse.journey_explanations``; it cannot add
exhibits, minutes or URLs. Session ownership and publication are revalidated in a fresh
transaction afterwards, so a withdrawal or session deletion during the provider call is never
published as current.
"""

import asyncio
import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, cast
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from folkverse import content
from folkverse.content import approved, published_exhibits
from folkverse.content_models import (
    Claim,
    ClaimEvidence,
    Exhibit,
    ExhibitRegion,
    Passage,
    Region,
    Source,
)
from folkverse.errors import ApiError
from folkverse.journey_explanations import (
    ALLOWED_REASON_CODES,
    JourneyExplainer,
    render_reason,
)
from folkverse.journey_explanations import MAX_STOPS as MAX_JOURNEY_STOPS
from folkverse.journey_models import JOURNEY_ID_PREFIX, Journey, JourneyStop
from folkverse.journey_planner import (
    MAX_DURATION,
    MAX_INTERESTS,
    MIN_DURATION,
    Candidate,
    NoticeCode,
    Selection,
    allowed_codes,
    matches_interests,
    normalise_interests,
    plan,
    reason_codes,
    render_notice,
    start_notice_code,
)
from folkverse.sessions import COOKIE_NAME, SessionService, require_owner

router = APIRouter(prefix="/api/v1")
Locale = Literal["en", "zh-CN"]
ExplanationStatus = Literal["deterministic", "generated", "unavailable"]

# Journey bodies are tiny: bounded interests, novelty IDs and ordered stop IDs only.
JOURNEY_BODY_LIMIT = 16384
MAX_ID_CHARS = 100
MAX_INTEREST_CHARS = 60
KNOWN_NOTICE_CODES: frozenset[str] = frozenset(
    {
        "no_candidates",
        "no_fit",
        "partial_fill",
        "start_too_long",
        "start_ineligible",
        "start_filtered",
        "cap",
        "stops_withdrawn",
        "stops_trimmed",
    }
)


class JourneyBodyLimitMiddleware:
    """Bound journey request bodies before JSON parsing, mirroring the guide boundary."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = str(scope.get("path", ""))
        if (
            scope["type"] != "http"
            or scope.get("method") not in {"POST", "PATCH"}
            or not (path == "/api/v1/journeys" or path.startswith("/api/v1/journeys/"))
        ):
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > JOURNEY_BODY_LIMIT:
                response = JSONResponse(
                    {
                        "error": {
                            "code": "context_too_large",
                            "message": "The journey request is too large.",
                            "retryable": False,
                        },
                        "request_id": scope.get("state", {}).get("request_id", "unavailable"),
                    },
                    status_code=413,
                    headers={"Cache-Control": "no-store"},
                )
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


def _clean_interests(values: list[str]) -> list[str]:
    if len(values) > MAX_INTERESTS:
        raise ValueError("too many interests")
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value.strip()
        if not text or len(text) > MAX_INTEREST_CHARS:
            raise ValueError("invalid interest")
        key = text.casefold()
        if key not in seen:
            seen.add(key)
            cleaned.append(text)
    return cleaned


def _clean_ids(values: list[str], *, limit: int) -> list[str]:
    if len(values) > limit:
        raise ValueError("too many identifiers")
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value.strip()
        if not text or len(text) > MAX_ID_CHARS:
            raise ValueError("invalid identifier")
        if text not in seen:
            seen.add(text)
            cleaned.append(text)
    return cleaned


class JourneyCreate(BaseModel):
    """Explicit preferences only; unknown fields such as an owner ID are rejected."""

    model_config = ConfigDict(extra="forbid", strict=True)

    interests: list[str] = Field(default_factory=list, max_length=MAX_INTERESTS)
    locale: Locale
    duration_minutes: int = Field(ge=MIN_DURATION, le=MAX_DURATION)
    region_id: str | None = Field(default=None, max_length=MAX_ID_CHARS)
    novelty_exhibit_ids: list[str] = Field(default_factory=list, max_length=MAX_JOURNEY_STOPS)
    start_exhibit_id: str | None = Field(default=None, max_length=MAX_ID_CHARS)

    @field_validator("interests")
    @classmethod
    def interests_are_bounded(cls, value: list[str]) -> list[str]:
        return _clean_interests(value)

    @field_validator("novelty_exhibit_ids")
    @classmethod
    def novelty_is_bounded(cls, value: list[str]) -> list[str]:
        return _clean_ids(value, limit=MAX_JOURNEY_STOPS)


class JourneyPatch(BaseModel):
    """An explicit ordered list is required: an empty list clears the route, ``{}`` is refused."""

    model_config = ConfigDict(extra="forbid", strict=True)

    ordered_exhibit_ids: list[str] = Field(max_length=MAX_JOURNEY_STOPS)
    expected_version: int | None = Field(default=None, ge=1)

    @field_validator("ordered_exhibit_ids")
    @classmethod
    def ordered_ids_are_bounded(cls, value: list[str]) -> list[str]:
        for item in value:
            if not item.strip() or len(item.strip()) > MAX_ID_CHARS:
                raise ValueError("invalid identifier")
        return [item.strip() for item in value]


class JourneySource(BaseModel):
    id: str
    title: str
    institution: str
    canonical_url: str


class JourneyStopCard(BaseModel):
    exhibit_id: str
    title: str
    summary: str
    estimated_minutes: int
    region_ids: list[str]
    themes: list[str]
    reason: str
    sources: list[JourneySource]


class JourneyResponse(BaseModel):
    id: str
    locale: Locale
    interests: list[str]
    duration_minutes: int
    region_id: str | None
    novelty_exhibit_ids: list[str]
    total_minutes: int
    version: int
    stops: list[JourneyStopCard]
    notice: str | None
    explanation_status: ExplanationStatus
    updated_at: datetime


class JourneyList(BaseModel):
    items: list[JourneyResponse]


@dataclass
class _Cache:
    regions: dict[str, tuple[str, ...]] = field(default_factory=dict)
    sources: dict[str, list[JourneySource]] = field(default_factory=dict)


@dataclass(frozen=True)
class _Corpus:
    rows: dict[str, Exhibit]
    candidates: dict[str, Candidate]


@dataclass
class _Resolved:
    stops: list[JourneyStopCard]
    total_minutes: int
    notice_codes: list[NoticeCode]
    notice: str | None


@dataclass
class _Prepared:
    """Everything the provider call needs, with no live ORM object held across the await."""

    journey_id: str
    owner_session: str
    version: int
    locale: str
    interests: list[str]
    payload: list[dict[str, Any]]
    stop_ids: list[str]
    signature: str
    total_minutes: int


def _sessions(request: Request) -> SessionService:
    service = getattr(request.app.state, "sessions", None)
    if isinstance(service, SessionService):
        return service
    return SessionService(request.app.state.settings)


def _explainer(request: Request) -> Any | None:
    """Return a ready explainer, or ``None`` for a deterministic-only deployment."""
    state = request.app.state
    existing = getattr(state, "journey_explainer", None)
    if existing is not None:
        return existing
    factory = getattr(state, "journey_explainer_factory", None)
    if factory is None:
        return None
    try:
        built = factory(request.app)
    except Exception:  # An optional enhancement must never break the deterministic route.
        return None
    if built is not None:
        state.journey_explainer = built
    return built


def build_journey_explainer(app: FastAPI) -> JourneyExplainer | None:
    """Build the optional explainer from the existing server-side gateway and settings.

    The readiness gates mirror ``GuideGateway._ready`` so an explainer is only built when the
    configured provider could actually answer: no key, wrong mode, disabled quota or an
    unpriced budget means the deterministic route is final and no call is attempted.
    """
    settings = getattr(app.state, "settings", None)
    gateway = getattr(app.state, "guide_gateway", None)
    if settings is None or gateway is None or settings.app_mode != "live":
        return None
    key = settings.provider_key
    if key is None or not key.get_secret_value().strip():
        return None
    if settings.guide_provider == "ollama":
        if settings.ollama_daily_request_limit <= 0:
            return None
    elif (
        settings.daily_ai_budget_usd <= 0
        or settings.deepseek_price_model != settings.deepseek_model
        or settings.deepseek_price_base_url != settings.deepseek_base_url
        or settings.deepseek_input_usd_per_million is None
        or settings.deepseek_output_usd_per_million is None
    ):
        return None
    try:
        return JourneyExplainer(
            gateway,
            max_entries=64,
            ttl_seconds=900.0,
            max_stops=MAX_JOURNEY_STOPS,
        )
    except (TypeError, ValueError):
        return None


def _localized(values: Any, locale: str) -> str:
    if isinstance(values, dict):
        for key in (locale, "en"):
            text = values.get(key)
            if isinstance(text, str) and text.strip():
                return text
    return ""


def _has_locale(values: Any, locale: str) -> bool:
    """Exact-locale availability; a fallback language never makes a stop eligible."""
    return bool(
        isinstance(values, dict)
        and isinstance(values.get(locale), str)
        and str(values[locale]).strip()
    )


def _available_locales(row: Exhibit) -> tuple[str, ...]:
    return tuple(
        locale
        for locale in ("en", "zh-CN")
        if _has_locale(row.title, locale) and _has_locale(row.summary, locale)
    )


def _region_ids(db: Session, exhibit_id: str, cache: _Cache) -> tuple[str, ...]:
    if exhibit_id not in cache.regions:
        cache.regions[exhibit_id] = tuple(
            sorted(
                db.scalars(
                    select(ExhibitRegion.region_id).where(ExhibitRegion.exhibit_id == exhibit_id)
                )
            )
        )
    return cache.regions[exhibit_id]


def _usable_url(url: str) -> bool:
    """Only a parsed absolute HTTPS URL is offered to the visitor as a source link."""
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return False
    return parts.scheme == "https" and bool(parts.netloc)


def _sources(db: Session, exhibit_id: str, cache: _Cache) -> list[JourneySource]:
    if exhibit_id in cache.sources:
        return cache.sources[exhibit_id]
    claim_ids = list(db.scalars(select(Claim.id).where(Claim.exhibit_id == exhibit_id)))
    source_ids: set[str] = set()
    if claim_ids:
        source_ids = set(
            db.scalars(
                select(Passage.source_id)
                .join(ClaimEvidence, ClaimEvidence.passage_id == Passage.id)
                .where(ClaimEvidence.claim_id.in_(claim_ids))
            )
        )
    items: list[JourneySource] = []
    if source_ids:
        for record in db.scalars(
            select(Source).where(Source.id.in_(source_ids)).order_by(Source.id)
        ):
            if approved(db, record) and _usable_url(record.canonical_url):
                items.append(
                    JourneySource(
                        id=record.id,
                        title=record.title,
                        institution=record.institution,
                        canonical_url=record.canonical_url,
                    )
                )
    cache.sources[exhibit_id] = items
    return items


def _minutes_in_range(row: Exhibit) -> bool:
    """Stored minutes must be a usable positive duration; anything else is not selectable."""
    return 1 <= row.estimated_minutes <= MAX_DURATION


def _corpus(db: Session, cache: _Cache | None = None) -> _Corpus:
    """Selectable exhibits: published, usable minutes, at least one approved HTTPS source."""
    cache = cache if cache is not None else _Cache()
    rows: dict[str, Exhibit] = {}
    candidates: dict[str, Candidate] = {}
    for row in published_exhibits(db):
        if not _minutes_in_range(row) or not _sources(db, row.id, cache):
            continue
        rows[row.id] = row
        candidates[row.id] = Candidate(
            id=row.id,
            estimated_minutes=row.estimated_minutes,
            themes=tuple(theme for theme in (row.themes or ()) if isinstance(theme, str)),
            region_ids=_region_ids(db, row.id, cache),
            locales=_available_locales(row),
        )
    return _Corpus(rows=rows, candidates=candidates)


def _status(value: str) -> ExplanationStatus:
    known = {"deterministic", "generated", "unavailable"}
    return cast(ExplanationStatus, value) if value in known else "deterministic"


def _stop_card(
    db: Session,
    candidate: Candidate,
    row: Exhibit,
    codes: Sequence[str],
    rendered_locale: str,
    cache: _Cache,
    *,
    is_start: bool,
) -> JourneyStopCard:
    # The starting label is positional truth, never a stale stored claim: it is rendered only for
    # the declared start while that stop really is first, and it returns if it is first again.
    chosen = {code for code in codes if code != "starting_exhibit"} or {"time_fit"}
    if is_start:
        chosen.add("starting_exhibit")
    effective = tuple(code for code in ALLOWED_REASON_CODES if code in chosen)
    return JourneyStopCard(
        exhibit_id=row.id,
        title=_localized(row.title, rendered_locale),
        summary=_localized(row.summary, rendered_locale),
        estimated_minutes=row.estimated_minutes,
        region_ids=list(candidate.region_ids),
        themes=[theme for theme in (row.themes or ()) if isinstance(theme, str)],
        reason=render_reason(effective, rendered_locale),
        sources=_sources(db, row.id, cache),
    )


def _resolve(
    db: Session,
    journey: Journey,
    *,
    rendered_locale: str,
    corpus: _Corpus,
    cache: _Cache,
) -> _Resolved:
    """Re-resolve stored stops against the current published corpus, pruning safely."""
    stored = list(
        db.scalars(
            select(JourneyStop)
            .where(JourneyStop.journey_id == journey.id)
            .order_by(JourneyStop.position)
        )
    )
    stops: list[JourneyStopCard] = []
    total = 0
    withdrawn = 0
    trimmed = 0
    for stop in stored:
        candidate = corpus.candidates.get(stop.exhibit_id)
        if candidate is None or rendered_locale not in candidate.locales:
            withdrawn += 1
            continue
        if not 1 <= candidate.estimated_minutes <= journey.duration_minutes:
            # Never let a stored row invent time: unusable minutes are pruned, never summed.
            withdrawn += 1
            continue
        if total + candidate.estimated_minutes > journey.duration_minutes:
            trimmed += 1
            continue
        stops.append(
            _stop_card(
                db,
                candidate,
                corpus.rows[candidate.id],
                tuple(stop.reason_codes or ()),
                rendered_locale,
                cache,
                is_start=not stops and journey.start_exhibit_id == candidate.id,
            )
        )
        total += candidate.estimated_minutes

    codes: list[NoticeCode] = []
    if withdrawn:
        codes.append("stops_withdrawn")
    if trimmed:
        codes.append("stops_trimmed")
    # The starting notice is re-derived from the exhibit as it is right now, so a stored claim can
    # never survive a withdrawal, a re-review or a shorter duration: it is replaced by the current
    # truth (start_ineligible when it is gone) or dropped once the exhibit fits again.
    start_minutes = 0
    start_id = journey.start_exhibit_id
    if start_id is not None:
        start = corpus.candidates.get(start_id)
        current = start_notice_code(
            start,
            interests=normalise_interests(list(journey.interests or [])),
            locale=rendered_locale,
            region_id=journey.region_id,
            duration_minutes=journey.duration_minutes,
        )
        if current is not None:
            codes.append(current)
        start_minutes = start.estimated_minutes if start is not None else 0
    for code in journey.notice_codes or []:
        if code in KNOWN_NOTICE_CODES and code not in codes and not code.startswith("start_"):
            codes.append(cast(NoticeCode, code))
    if not stops:
        codes = [code for code in codes if code != "partial_fill"]
    notice = render_notice(
        codes,
        rendered_locale,
        duration_minutes=journey.duration_minutes,
        total_minutes=total,
        withdrawn=withdrawn,
        trimmed=trimmed,
        start_minutes=start_minutes,
    )
    return _Resolved(stops=stops, total_minutes=total, notice_codes=codes, notice=notice)


def _response(
    db: Session,
    journey: Journey,
    *,
    rendered_locale: str,
    corpus: _Corpus,
    cache: _Cache,
) -> JourneyResponse:
    resolved = _resolve(db, journey, rendered_locale=rendered_locale, corpus=corpus, cache=cache)
    return JourneyResponse(
        id=journey.id,
        locale=cast(
            Locale, rendered_locale if rendered_locale in {"en", "zh-CN"} else journey.locale
        ),
        interests=list(journey.interests or []),
        duration_minutes=journey.duration_minutes,
        region_id=journey.region_id,
        novelty_exhibit_ids=list(journey.novelty_exhibit_ids or []),
        total_minutes=resolved.total_minutes,
        version=journey.version,
        stops=resolved.stops,
        notice=resolved.notice,
        explanation_status=_status(journey.explanation_status),
        updated_at=journey.updated_at,
    )


def _write_stops(
    db: Session, journey_id: str, entries: Sequence[tuple[str, Sequence[str]]]
) -> None:
    db.execute(delete(JourneyStop).where(JourneyStop.journey_id == journey_id))
    db.flush()
    for position, (exhibit_id, codes) in enumerate(entries):
        db.add(
            JourneyStop(
                journey_id=journey_id,
                position=position,
                exhibit_id=exhibit_id,
                reason_codes=list(codes),
            )
        )
    db.flush()


def _corpus_signature(
    db: Session, exhibit_ids: Sequence[str], locale: str, interests: Sequence[str]
) -> str:
    """Stable hash of reviewed metadata for the selected stops; invalidates the model cache."""
    parts: list[str] = []
    for exhibit_id in sorted(set(exhibit_ids)):
        row = db.get(Exhibit, exhibit_id)
        if row is None:
            continue
        parts.append(f"{exhibit_id}:{content.fingerprint(db, row)}")
        claim_ids = list(db.scalars(select(Claim.id).where(Claim.exhibit_id == exhibit_id)))
        passage_ids: set[str] = set()
        if claim_ids:
            passage_ids = set(
                db.scalars(
                    select(ClaimEvidence.passage_id).where(ClaimEvidence.claim_id.in_(claim_ids))
                )
            )
        for passage_id in sorted(passage_ids):
            passage = db.get(Passage, passage_id)
            if passage is not None:
                parts.append(f"{passage_id}:{content.fingerprint(db, passage)}")
    payload = json.dumps(
        {"stops": parts, "locale": locale, "interests": list(interests)},
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _prepare_journey(request: Request, body: JourneyCreate) -> _Prepared:
    """Validate, select and store the deterministic route; no provider call here."""
    with Session(request.app.state.engine) as db:
        session = _sessions(request).require(request.cookies.get(COOKIE_NAME), db)
        cache = _Cache()
        corpus = _corpus(db, cache)
        if body.region_id is not None and db.get(Region, body.region_id) is None:
            # A real region with no published exhibit yet is an honest empty route, not an error.
            raise ApiError(422, "unknown_region", "That region is not a known museum region.")
        if body.start_exhibit_id is not None and body.start_exhibit_id not in corpus.candidates:
            raise ApiError(422, "unknown_exhibit", "The starting exhibit is not published.")

        result = plan(
            list(corpus.candidates.values()),
            interests=body.interests,
            locale=body.locale,
            duration_minutes=body.duration_minutes,
            region_id=body.region_id,
            novelty_exhibit_ids=body.novelty_exhibit_ids,
            start_exhibit_id=body.start_exhibit_id,
        )
        now = datetime.now(UTC)
        journey = Journey(
            id=f"{JOURNEY_ID_PREFIX}{uuid4().hex}",
            owner_session=session.id,
            locale=body.locale,
            interests=body.interests,
            duration_minutes=body.duration_minutes,
            region_id=body.region_id,
            novelty_exhibit_ids=body.novelty_exhibit_ids,
            start_exhibit_id=body.start_exhibit_id,
            total_minutes=result.total_minutes,
            version=1,
            explanation_status="deterministic",
            notice_codes=list(result.notice_codes),
            created_at=now,
            updated_at=now,
        )
        db.add(journey)
        db.flush()
        _write_stops(
            db,
            journey.id,
            [(selection.candidate.id, selection.codes) for selection in result.selections],
        )
        db.commit()
        payload = _explanation_payload(
            journey, result.selections, body.locale, corpus
        )
        stop_ids = [selection.candidate.id for selection in result.selections]
        signature = _corpus_signature(db, stop_ids, body.locale, body.interests)
        return _Prepared(
            journey_id=journey.id,
            owner_session=session.id,
            version=journey.version,
            locale=body.locale,
            interests=list(body.interests),
            payload=payload,
            stop_ids=stop_ids,
            signature=signature,
            total_minutes=result.total_minutes,
        )


def _explanation_payload(
    journey: Journey, selections: Sequence[Selection], rendered_locale: str, corpus: _Corpus
) -> list[dict[str, Any]]:
    interest_set = normalise_interests(list(journey.interests or []))
    novelty = frozenset(
        item.strip().casefold() for item in (journey.novelty_exhibit_ids or []) if item.strip()
    )
    payload: list[dict[str, Any]] = []
    for selection in selections:
        row = corpus.rows[selection.candidate.id]
        payload.append(
            {
                "exhibit_id": row.id,
                "title": _localized(row.title, rendered_locale),
                "summary": _localized(row.summary, rendered_locale),
                "themes": [theme for theme in (row.themes or ()) if isinstance(theme, str)],
                "estimated_minutes": row.estimated_minutes,
                "allowed_reason_codes": list(
                    allowed_codes(
                        selection.candidate,
                        interests=interest_set,
                        novelty_exhibit_ids=novelty,
                        start_exhibit_id=journey.start_exhibit_id,
                    )
                ),
                "fallback_reason": render_reason(selection.codes, rendered_locale),
            }
        )
    return payload


async def _explain_route(
    request: Request, prepared: _Prepared
) -> tuple[dict[str, tuple[str, ...]], ExplanationStatus]:
    """Optionally upgrade deterministic stop codes with validated model selections."""
    explainer = _explainer(request)
    if explainer is None or not prepared.payload:
        return {}, "deterministic"
    try:
        result = await explainer.explain(
            prepared.payload,
            prepared.locale,
            prepared.interests,
            prepared.owner_session,
            prepared.signature,
        )
    except Exception:  # Provider and transport faults are an unavailable enhancement only.
        return {}, "unavailable"
    codes = getattr(result, "codes", None)
    if getattr(result, "status", None) != "generated" or not isinstance(codes, dict):
        return {}, "unavailable"
    if set(codes) != set(prepared.stop_ids):
        return {}, "unavailable"
    known = set(ALLOWED_REASON_CODES)
    cleaned: dict[str, tuple[str, ...]] = {}
    for exhibit_id, value in codes.items():
        supplied = set(value or ())
        chosen = tuple(code for code in ALLOWED_REASON_CODES if code in supplied)
        if not chosen or not supplied <= known:
            return {}, "unavailable"
        cleaned[exhibit_id] = chosen
    return cleaned, "generated"


def _finish_journey(
    request: Request,
    prepared: _Prepared,
    codes: dict[str, tuple[str, ...]],
    status: ExplanationStatus,
) -> JourneyResponse:
    """Revalidate ownership/publication in a fresh transaction, then persist or skip codes."""
    with Session(request.app.state.engine) as db:
        session = _sessions(request).require(request.cookies.get(COOKIE_NAME), db)
        cache = _Cache()
        corpus = _corpus(db, cache)
        # Lock the row so the expected-version check and the write are one serialized step.
        row = db.scalars(
            select(Journey).where(Journey.id == prepared.journey_id).with_for_update()
        ).one_or_none()
        if row is None or row.owner_session != session.id:
            raise ApiError(404, "not_found", "Journey not found.")
        if row.version != prepared.version:
            # A concurrent edit landed during the provider call; never overwrite it with labels
            # computed for the previous route.
            return _response(db, row, rendered_locale=prepared.locale, corpus=corpus, cache=cache)
        stops = list(db.scalars(select(JourneyStop).where(JourneyStop.journey_id == row.id)))
        if codes and set(codes) <= set(corpus.candidates) and set(codes) <= set(prepared.stop_ids):
            for stop in stops:
                chosen = codes.get(stop.exhibit_id)
                if chosen is not None:
                    stop.reason_codes = list(chosen)
            row.explanation_status = status
        else:
            row.explanation_status = "unavailable" if codes else status
        db.commit()
        return _response(db, row, rendered_locale=prepared.locale, corpus=corpus, cache=cache)


@router.post("/journeys", response_model=JourneyResponse, operation_id="create_journey")
async def create_journey(request: Request, body: JourneyCreate) -> JourneyResponse:
    prepared = await asyncio.to_thread(_prepare_journey, request, body)
    codes, status = await _explain_route(request, prepared)
    return await asyncio.to_thread(_finish_journey, request, prepared, codes, status)


@router.get("/journeys", response_model=JourneyList, operation_id="journeys")
def journeys(
    request: Request,
    locale: Locale | None = None,
    limit: int = Query(default=10, ge=1, le=20),
) -> JourneyList:
    with Session(request.app.state.engine) as db:
        session = _sessions(request).require(request.cookies.get(COOKIE_NAME), db)
        cache = _Cache()
        corpus = _corpus(db, cache)
        rows = list(
            db.scalars(
                select(Journey)
                .where(Journey.owner_session == session.id)
                .order_by(Journey.updated_at.desc(), Journey.id.desc())
                .limit(limit)
            )
        )
        return JourneyList(
            items=[
                _response(
                    db,
                    journey,
                    rendered_locale=locale or journey.locale,
                    corpus=corpus,
                    cache=cache,
                )
                for journey in rows
            ]
        )


@router.get("/journeys/{identifier}", response_model=JourneyResponse, operation_id="journey")
def journey(request: Request, identifier: str, locale: Locale | None = None) -> JourneyResponse:
    with Session(request.app.state.engine) as db:
        session = _sessions(request).require(request.cookies.get(COOKIE_NAME), db)
        row = db.get(Journey, identifier)
        if row is None:
            raise ApiError(404, "not_found", "Journey not found.")
        require_owner(row.owner_session, session)
        cache = _Cache()
        corpus = _corpus(db, cache)
        return _response(db, row, rendered_locale=locale or row.locale, corpus=corpus, cache=cache)


@router.patch(
    "/journeys/{identifier}", response_model=JourneyResponse, operation_id="update_journey"
)
def update_journey(
    request: Request,
    identifier: str,
    body: JourneyPatch,
    locale: Locale | None = None,
) -> JourneyResponse:
    with Session(request.app.state.engine) as db:
        session = _sessions(request).require(request.cookies.get(COOKIE_NAME), db)
        # Serialize concurrent edits: the version check and the write share one locked row.
        row = db.scalars(
            select(Journey).where(Journey.id == identifier).with_for_update()
        ).one_or_none()
        if row is None:
            raise ApiError(404, "not_found", "Journey not found.")
        require_owner(row.owner_session, session)
        if body.expected_version is not None and body.expected_version != row.version:
            raise ApiError(409, "stale_state", "This journey changed since you loaded it.")

        ordered = body.ordered_exhibit_ids
        if len(set(ordered)) != len(ordered):
            raise ApiError(422, "duplicate_exhibit", "A stop is listed more than once.")

        # A write must be legal for the route's stored preferences *and* renderable in the language
        # this response is asked for, so a 200 always contains exactly the stops that were sent.
        display_locale = locale or row.locale
        cache = _Cache()
        corpus = _corpus(db, cache)
        interest_set = normalise_interests(list(row.interests or []))
        for exhibit_id in ordered:
            candidate = corpus.candidates.get(exhibit_id)
            if candidate is None or row.locale not in candidate.locales:
                raise ApiError(422, "unknown_exhibit", "A stop is not a published exhibit.")
            if display_locale not in candidate.locales:
                raise ApiError(
                    422,
                    "invalid_input",
                    "A stop is not available in the requested display language.",
                )
            if row.region_id is not None and row.region_id not in candidate.region_ids:
                raise ApiError(422, "invalid_input", "A stop is outside this route's region.")
            if not matches_interests(candidate, interest_set):
                raise ApiError(
                    422, "invalid_input", "A stop does not match this route's interests."
                )
        total = sum(corpus.candidates[exhibit_id].estimated_minutes for exhibit_id in ordered)
        if total > row.duration_minutes:
            raise ApiError(
                422,
                "exceeds_duration",
                f"These stops need {total} minutes, more than the {row.duration_minutes} allowed.",
            )

        previous = {
            stop.exhibit_id: tuple(stop.reason_codes or ())
            for stop in db.scalars(select(JourneyStop).where(JourneyStop.journey_id == row.id))
        }
        reorder_only = set(ordered) == set(previous)
        novelty = frozenset(
            item.strip().casefold() for item in (row.novelty_exhibit_ids or []) if item.strip()
        )
        entries: list[tuple[str, Sequence[str]]] = []
        for position, exhibit_id in enumerate(ordered):
            candidate = corpus.candidates[exhibit_id]
            codes = previous.get(exhibit_id)
            if not reorder_only or codes is None:
                # Any composition change re-derives every stop deterministically, so the
                # "deterministic" status and the rendered reasons always agree.
                codes = reason_codes(
                    candidate,
                    interests=interest_set,
                    novelty_exhibit_ids=novelty,
                    start_exhibit_id=row.start_exhibit_id,
                )
            if position != 0 or exhibit_id != row.start_exhibit_id:
                codes = tuple(code for code in codes if code != "starting_exhibit") or ("time_fit",)
            entries.append((exhibit_id, codes))
        _write_stops(db, row.id, entries)
        row.version += 1
        row.total_minutes = total
        row.updated_at = datetime.now(UTC)
        if not reorder_only:
            row.explanation_status = "deterministic"
        db.commit()
        return _response(db, row, rendered_locale=display_locale, corpus=corpus, cache=cache)
