from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError
from sqlalchemy import delete, text
from sqlalchemy.orm import Session

from folkverse.config import Settings
from folkverse.database import AnonymousSession
from folkverse.errors import ApiError
from folkverse.main import create_app
from folkverse.sessions import COOKIE_NAME, SessionService, require_owner

ORIGIN = {"Origin": "http://localhost:3000"}


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app(Settings().model_copy(update={"app_mode": "demo"}))
    ids: list[str] = []
    with TestClient(app) as test_client:
        test_client.owned_ids = ids
        yield test_client
        with Session(app.state.engine) as db:
            if ids:
                db.execute(delete(AnonymousSession).where(AnonymousSession.id.in_(ids)))
                db.commit()


def start(client: TestClient) -> str:
    response = client.post("/api/v1/session", headers=ORIGIN)
    assert response.status_code == 200
    assert response.json()["behavioral_opt_in"] is False
    session_id = response.json()["session_id"]
    client.owned_ids.append(session_id)
    return session_id


def test_database_vector_and_migration_are_real(client: TestClient) -> None:
    for endpoint in ("/health", "/api/v1/health"):
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.json()["database"] == "available"
        assert response.json()["pgvector"] == "available"
        assert response.json()["schema_status"] == "current"
        assert response.headers["cache-control"] == "no-store"
    with client.app.state.engine.connect() as db:
        assert db.execute(text("SELECT '[1,2,3]'::vector <-> '[1,2,3]'::vector")).scalar() == 0


def test_database_outage_is_not_success() -> None:
    settings = Settings().model_copy(
        update={
            "database_url": SecretStr("postgresql+psycopg://blocked:hidden@127.0.0.1:9/unavailable")
        }
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 503
        assert response.json()["status"] == "degraded"
        assert response.json()["database"] == "unavailable"
        failed = client.post("/api/v1/session", headers=ORIGIN)
        assert failed.status_code == 503
        assert failed.json()["error"]["code"] == "database_unavailable"
        assert "hidden" not in failed.text
        assert "postgresql" not in failed.text


def test_session_cookie_reuse_and_revocation(client: TestClient) -> None:
    assert client.get("/api/v1/session").status_code == 401
    session_id = start(client)
    token = client.cookies.get(COOKIE_NAME)
    assert client.get("/api/v1/session").json()["session_id"] == session_id
    assert client.post("/api/v1/session", headers=ORIGIN).json()["session_id"] == session_id
    assert client.delete("/api/v1/session", headers=ORIGIN).status_code == 200
    assert client.cookies.get(COOKIE_NAME) is None
    client.cookies.set(COOKIE_NAME, token)
    assert client.get("/api/v1/session").status_code == 401


def test_cookie_flags_and_mode_isolation(client: TestClient) -> None:
    response = client.post("/api/v1/session", headers=ORIGIN)
    client.owned_ids.append(response.json()["session_id"])
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie and "path=/" in cookie
    live = Settings().model_copy(update={"app_mode": "live", "cookie_secure": True})
    with TestClient(create_app(live), base_url="https://localhost") as secure:
        response = secure.post("/api/v1/session", headers=ORIGIN)
        client.owned_ids.append(response.json()["session_id"])
        assert "secure" in response.headers["set-cookie"].lower()
        live_token = secure.cookies.get(COOKIE_NAME)
    client.cookies.clear()
    client.cookies.set(COOKIE_NAME, live_token)
    assert client.get("/api/v1/session").status_code == 401


def test_tampered_and_expired_session_rejected(client: TestClient) -> None:
    session_id = start(client)
    token = client.cookies.get(COOKIE_NAME)
    client.cookies.clear()
    client.cookies.set(COOKIE_NAME, token + "tampered")
    assert client.get("/api/v1/session").status_code == 401
    client.cookies.set(COOKIE_NAME, token)
    with Session(client.app.state.engine) as db:
        record = db.get(AnonymousSession, session_id)
        record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()
    assert client.get("/api/v1/session").status_code == 401


def test_origin_guard_and_cors(client: TestClient) -> None:
    start(client)
    for origin in ({}, {"Origin": "https://attacker.example"}, {"Origin": "null"}):
        assert client.delete("/api/v1/session", headers=origin).status_code == 403
    response = client.options(
        "/api/v1/session",
        headers={
            **ORIGIN,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers["access-control-allow-origin"] == ORIGIN["Origin"]
    bad = client.options(
        "/api/v1/session",
        headers={
            "Origin": "https://attacker.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in bad.headers


def test_ownership_is_server_derived(client: TestClient) -> None:
    first = start(client)
    client.cookies.clear()
    second = start(client)
    assert first != second
    with Session(client.app.state.engine) as db:
        current = SessionService(client.app.state.settings).require(
            client.cookies.get(COOKIE_NAME), db
        )
        require_owner(second, current)
        with pytest.raises(ApiError) as error:
            require_owner(first, current)
        assert error.value.status == 403


def test_errors_are_sanitized_and_request_identified(client: TestClient) -> None:
    response = client.get("/api/v1/not-a-route")
    assert response.status_code == 404
    assert response.json()["request_id"] == response.headers["x-request-id"]
    assert set(response.json()) == {"error", "request_id"}
    assert Settings().session_secret.get_secret_value() not in response.text


@pytest.mark.parametrize(
    "origins", [["*"], ["http://localhost:3000/evil"], ["https://*.example"], []]
)
def test_invalid_origin_configuration_fails_closed(origins: list[str]) -> None:
    with pytest.raises(ValidationError):
        Settings(allowed_origins=origins)
