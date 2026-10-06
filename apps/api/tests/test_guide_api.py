"""Owned HTTP/SSE boundary tests; synthetic evidence, no live database/provider."""

import asyncio
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from test_guide_harness import db as db  # noqa: F401
from test_guide_harness import request
from test_guide_harness import service as service

from folkverse.config import Settings
from folkverse.errors import ApiError
from folkverse.guide_api import GuideRequestLimits, GuideVisit, guide_visit, stream_answer
from folkverse.main import create_app

ORIGIN = {"Origin": "http://localhost:3000"}


def setup_client(service, recheck=lambda: None):
    app = create_app(Settings().model_copy(update={"app_mode": "live"}))
    app.state.guide_harness = service[0]
    app.dependency_overrides[guide_visit] = lambda: GuideVisit("visit_fixture", recheck)
    return TestClient(app)


def frames(response):
    return [
        (part.splitlines()[0][7:], json.loads(part.splitlines()[1][6:]))
        for part in response.text.strip().split("\n\n")
    ]


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_owned_json_and_sse_checked_answer(service, locale):
    with setup_client(service) as client:
        body = request(locale).model_dump()
        result = client.post("/api/v1/guide", json=body, headers=ORIGIN)
        assert result.status_code == 200
        assert result.json()["claims"][0]["text"] == result.json()["sources"][0]["text"]
        result = client.post(
            "/api/v1/guide", json=body, headers={**ORIGIN, "Accept": "text/event-stream"}
        )
        assert result.status_code == 200 and result.headers["cache-control"] == "no-store"
        events = frames(result)
        names = [name for name, _ in events]
        assert names[0] == "meta" and names[-3:] == ["answer", "sources", "done"]
        assert any(name == "status" and body["stage"] == "generating" for name, body in events)
        answer, sources, done = [body for _, body in events[-3:]]
        assert "sources" not in answer
        assert sources["items"][0]["text"] == answer["claims"][0]["text"]
        assert answer["answer_id"] == done["answer_id"] == sources["answer_id"]
        assert done["first_meaningful_content_ms"] >= 0
        assert all(body["mode"] == "live" for name, body in events if name == "meta")


@pytest.mark.parametrize("code", ["provider_auth", "provider_timeout", "budget_exhausted"])
def test_failure_terminal_stream_has_no_answer(service, code):
    service[2].failure = ApiError(503, code, "Guide unavailable", True)
    with setup_client(service) as client:
        events = frames(
            client.post(
                "/api/v1/guide",
                json=request().model_dump(),
                headers={**ORIGIN, "Accept": "text/event-stream"},
            )
        )
        assert events[-1][0] == "error" and events[-1][1]["error"]["code"] == code
        assert not any(name in {"answer", "sources", "done"} for name, _ in events)


def test_recheck_ownership_before_publication(service):
    def revoked():
        raise ApiError(401, "session_expired", "Session expired")

    with setup_client(service, revoked) as client:
        events = frames(
            client.post(
                "/api/v1/guide",
                json=request().model_dump(),
                headers={**ORIGIN, "Accept": "text/event-stream"},
            )
        )
        assert events[-1][0] == "error"
        assert events[-1][1]["error"]["code"] == "session_expired"
        assert not any(name == "answer" for name, _ in events)


def test_recheck_evidence_after_session_check(service):
    def withdraw():
        service[1].is_current = False

    with setup_client(service, withdraw) as client:
        result = client.post("/api/v1/guide", json=request().model_dump(), headers=ORIGIN)
        assert result.status_code == 409 and result.json()["error"]["code"] == "evidence_changed"


def test_insufficiency_has_no_meaningful_answer_latency(service):
    with setup_client(service) as client:
        events = frames(
            client.post(
                "/api/v1/guide",
                json=request(question="Invented dynasty history").model_dump(),
                headers={**ORIGIN, "Accept": "text/event-stream"},
            )
        )
        assert events[-3][1]["status"] == "insufficient"
        assert events[-2][1]["items"] == []
        assert events[-1][1]["first_meaningful_content_ms"] is None
        assert service[2].calls == 0


def test_origin_input_and_limits(service):
    with setup_client(service) as client:
        assert client.post("/api/v1/guide", json=request().model_dump()).status_code == 403
        assert (
            client.post("/api/v1/guide", json={"question": " "}, headers=ORIGIN).status_code == 422
        )
        client.app.state.guide_request_limits = GuideRequestLimits("s" * 40, 1, 2)
        assert (
            client.post("/api/v1/guide", json=request().model_dump(), headers=ORIGIN).status_code
            == 200
        )
        response = client.post("/api/v1/guide", json=request().model_dump(), headers=ORIGIN)
        assert response.status_code == 429 and response.json()["error"]["code"] == "rate_limited"
        assert service[2].calls == 1


@pytest.mark.parametrize("mode, expected", [("demo", 503), ("live", 401)])
def test_missing_cookie_and_demo_rejected_before_database(mode, expected):
    with TestClient(create_app(Settings().model_copy(update={"app_mode": mode}))) as client:
        assert (
            client.post("/api/v1/guide", json=request().model_dump(), headers=ORIGIN).status_code
            == expected
        )


def test_disconnect_cancels_pending_harness():
    async def check():
        started = asyncio.Event()
        cancelled = asyncio.Event()

        class Harness:
            async def answer(self, *args, **kwargs):
                started.set()
                try:
                    await asyncio.sleep(100)
                finally:
                    cancelled.set()

        class Request:
            app = SimpleNamespace(state=SimpleNamespace(guide_harness=Harness()))
            state = SimpleNamespace(request_id="request_fixture")

            async def is_disconnected(self):
                await started.wait()
                return True

        events = [
            frame
            async for frame in stream_answer(
                Request(), request(), GuideVisit("visit_fixture", lambda: None)
            )
        ]
        assert len(events) == 1 and "event: meta" in events[0]
        assert cancelled.is_set()

    asyncio.run(check())


def test_stream_unexpected_exception_sanitized(service):
    def crash():
        raise RuntimeError("secret-provider-diagnostic")

    with setup_client(service, crash) as client:
        result = client.post(
            "/api/v1/guide",
            json=request().model_dump(),
            headers={**ORIGIN, "Accept": "text/event-stream"},
        )
        assert "secret-provider-diagnostic" not in result.text
        assert frames(result)[-1][1]["error"]["code"] == "guide_unavailable"
