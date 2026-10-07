"""Owned guide requests; progress may stream, factual text waits for validation."""

import asyncio
import hashlib
import hmac
import json
import re
import threading
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from folkverse.errors import ApiError
from folkverse.guide_harness import GuideAnswer, GuideRequest
from folkverse.guide_retrieval import EvidenceBundle, EvidencePassage, eligible_evidence
from folkverse.liaoning_publication import published_unit_evidence
from folkverse.sessions import COOKIE_NAME, SessionService

router = APIRouter(prefix="/api/v1")


class GuideBodyLimitMiddleware:
    """Bound the guide body before JSON parsing, including chunked requests."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope.get("path") != "/api/v1/guide"
            or scope.get("method") != "POST"
        ):
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > 65536:
                response = JSONResponse(
                    {
                        "error": {
                            "code": "context_too_large",
                            "message": "The guide context is too large.",
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


@dataclass
class GuideVisit:
    identifier: str
    recheck: Callable[[], None]


def guide_visit(request: Request) -> GuideVisit:
    settings = request.app.state.settings
    if settings.app_mode != "live":
        raise ApiError(
            503, "guide_unavailable", "Live guide requests are unavailable in demo mode."
        )
    cookie = request.cookies.get(COOKIE_NAME)
    sessions = SessionService(settings)
    with Session(request.app.state.engine) as db:
        identifier = sessions.require(cookie, db).id

    def recheck() -> None:
        with Session(request.app.state.engine) as db:
            if sessions.require(cookie, db).id != identifier:
                raise ApiError(403, "ownership_denied", "The guide session is unavailable.")

    return GuideVisit(identifier, recheck)


class GuideRequestLimits:
    """Bound cheap requests per worker; provider admission is also shared/persistent."""

    def __init__(self, secret: str, per_visit: int, global_limit: int) -> None:
        self.secret, self.per_visit, self.global_limit = secret, per_visit, global_limit
        self.recent: list[tuple[float, str]] = []
        self.lock = threading.Lock()

    def admit(self, identifier: str) -> None:
        owner = hmac.new(self.secret.encode(), identifier.encode(), hashlib.sha256).hexdigest()
        now = time.monotonic()
        with self.lock:
            self.recent = [(stamp, key) for stamp, key in self.recent if stamp > now - 60]
            if (
                len(self.recent) >= self.global_limit
                or sum(key == owner for _, key in self.recent) >= self.per_visit
            ):
                raise ApiError(429, "rate_limited", "The guide request limit was reached.", True)
            self.recent.append((now, owner))


def event(name: str, data: Any) -> str:
    return f"event: {name}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def run_checked(
    request: Request,
    payload: GuideRequest,
    visit: GuideVisit,
    progress: Callable[[str], None] | None = None,
) -> GuideAnswer:
    answer: GuideAnswer = await request.app.state.guide_harness.answer(
        payload,
        visit.identifier,
        progress=progress,
    )
    await asyncio.to_thread(visit.recheck)
    if answer.status == "answered":
        current = await asyncio.to_thread(
            request.app.state.guide_harness.repository.current,
            EvidenceBundle(
                locale=answer.locale,
                corpus_version=answer.corpus_version,
                passages=[p for p in answer.sources if p.evidence_origin != "official_lookup"],
                status="evidence_found",
            ),
        )
        if not current:
            raise ApiError(409, "evidence_changed", "The evidence changed. Please ask again.", True)
    for passage in answer.sources:
        if (
            passage.evidence_origin == "official_lookup"
            and not await request.app.state.guide_lookup.current(passage, refresh=True)
        ):
            raise ApiError(
                409, "evidence_changed", "The official source changed. Please ask again.", True
            )
    return answer


async def stream_answer(
    request: Request,
    payload: GuideRequest,
    visit: GuideVisit,
) -> AsyncIterator[str]:
    started = getattr(request.state, "guide_started_at", time.monotonic())
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=8)
    task = asyncio.create_task(run_checked(request, payload, visit, queue.put_nowait))
    request_id = request.state.request_id
    try:
        yield event("meta", {"request_id": request_id, "mode": "live", "corpus_version": None})
        while not task.done():
            if await request.is_disconnected():
                return
            try:
                status = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield event("status", {"stage": status})
            except TimeoutError:
                pass
        answer = task.result()
        yield event(
            "meta",
            {
                "request_id": request_id,
                "mode": "live",
                "corpus_version": answer.corpus_version,
                "retrieval_mode": answer.retrieval_mode,
                "harness_version": answer.harness_version,
            },
        )
        # Only the checked answer and its inspected evidence cross this boundary.
        first_content_ms = int((time.monotonic() - started) * 1000)
        yield event("answer", answer.model_dump(mode="json", exclude={"sources"}))
        yield event(
            "sources",
            {
                "answer_id": answer.answer_id,
                "items": [s.model_dump(mode="json") for s in answer.sources],
            },
        )
        yield event(
            "done",
            {
                "answer_id": answer.answer_id,
                "first_meaningful_content_ms": first_content_ms
                if answer.status == "answered"
                else None,
                "response_content_ms": first_content_ms,
            },
        )
    except ApiError as exc:
        yield event(
            "error",
            {
                "error": {"code": exc.code, "message": exc.message, "retryable": exc.retryable},
                "request_id": request_id,
            },
        )
    except SQLAlchemyError:
        yield event(
            "error",
            {
                "error": {
                    "code": "database_unavailable",
                    "message": "The museum service is temporarily unavailable.",
                    "retryable": True,
                },
                "request_id": request_id,
            },
        )
    except Exception:
        yield event(
            "error",
            {
                "error": {
                    "code": "guide_unavailable",
                    "message": "The guide is temporarily unavailable.",
                    "retryable": True,
                },
                "request_id": request_id,
            },
        )
    finally:
        if not task.done():
            task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass


@router.post(
    "/guide",
    response_model=GuideAnswer,
    operation_id="guide",
    responses={
        200: {"content": {"text/event-stream": {}}},
        401: {"description": "Anonymous session required"},
        429: {"description": "Request or provider limit reached"},
        503: {"description": "Guide unavailable"},
    },
)
async def guide(
    payload: GuideRequest,
    request: Request,
    visit: Annotated[GuideVisit, Depends(guide_visit)],
) -> GuideAnswer | StreamingResponse:
    request.app.state.guide_request_limits.admit(visit.identifier)
    if "text/event-stream" in request.headers.get("accept", ""):
        return StreamingResponse(
            stream_answer(request, payload, visit),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )
    task = asyncio.create_task(run_checked(request, payload, visit))
    try:
        while not task.done():
            if await request.is_disconnected():
                raise ApiError(499, "request_cancelled", "The guide request was cancelled.")
            await asyncio.sleep(0.05)
        return task.result()
    finally:
        if not task.done():
            task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass


class GuideEvidenceState(BaseModel):
    current: bool
    passage: EvidencePassage | None = None


@router.get("/guide/evidence/{identifier}", response_model=GuideEvidenceState)
async def inspect_guide_evidence(
    identifier: str, request: Request, visit: Annotated[GuideVisit, Depends(guide_visit)]
) -> GuideEvidenceState:
    if len(identifier) > 100 or not re.fullmatch(r"[a-zA-Z0-9_-]+", identifier):
        raise ApiError(422, "invalid_input", "The evidence identifier is invalid.")
    await asyncio.to_thread(visit.recheck)
    if identifier.startswith("lookup_"):
        lookup = request.app.state.guide_lookup
        entry = lookup.cache.get(identifier)
        if entry and await lookup.current(entry[1], refresh=True):
            return GuideEvidenceState(current=True, passage=entry[1])
        return GuideEvidenceState(current=False)

    def inspected() -> EvidencePassage | None:
        if identifier.startswith("unit_"):
            return next((p for p in published_unit_evidence() if p.passage_id == identifier), None)
        with Session(request.app.state.engine) as db:
            return next((p for p in eligible_evidence(db) if p.passage_id == identifier), None)

    passage = await asyncio.to_thread(inspected)
    return GuideEvidenceState(current=passage is not None, passage=passage)
