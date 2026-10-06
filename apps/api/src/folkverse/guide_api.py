"""Owned guide requests; progress may stream, factual text waits for validation."""

import asyncio
import hashlib
import hmac
import json
import threading
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from folkverse.errors import ApiError
from folkverse.guide_harness import GuideAnswer, GuideRequest
from folkverse.guide_retrieval import EvidenceBundle
from folkverse.sessions import COOKIE_NAME, SessionService

router = APIRouter(prefix="/api/v1")


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
                passages=answer.sources,
                status="evidence_found",
            ),
        )
        if not current:
            raise ApiError(409, "evidence_changed", "The evidence changed. Please ask again.", True)
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
