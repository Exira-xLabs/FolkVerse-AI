"""Real PostgreSQL journey locking/migration checks in a disposable database; no inference."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from test_postgres_integration import postgres as postgres  # noqa: F401

from folkverse.journey_models import Journey, JourneyStop
from folkverse.main import create_app

ORIGIN = {"Origin": "http://localhost:3000"}


def test_parallel_patches_serialize_expected_version_and_session_delete_cascades(postgres):
    engine, settings = postgres
    app = create_app(settings.model_copy(update={"app_mode": "demo"}))
    app.state.engine.dispose()
    app.state.engine = engine
    app.state.journey_explainer_factory = None
    with TestClient(app) as owner:
        assert owner.post("/api/v1/session", headers=ORIGIN).status_code == 200
        created = owner.post(
            "/api/v1/journeys",
            json={"locale": "en", "interests": [], "duration_minutes": 5},
            headers=ORIGIN,
        )
        assert created.status_code == 200
        journey = created.json()
        assert journey["version"] == 1 and len(journey["stops"]) == 1
        identifier = journey["id"]
        stop_ids = [stop["exhibit_id"] for stop in journey["stops"]]
        cookies = dict(owner.cookies)
        gate = Barrier(2)

        def patch(ids):
            # Separate HTTP clients, the same signed owner session, and simultaneous stale inputs.
            with TestClient(app) as editor:
                editor.cookies.update(cookies)
                gate.wait(timeout=10)
                return editor.patch(
                    f"/api/v1/journeys/{identifier}",
                    json={"ordered_exhibit_ids": ids, "expected_version": 1},
                    headers=ORIGIN,
                )

        with ThreadPoolExecutor(max_workers=2) as workers:
            responses = list(workers.map(patch, [stop_ids, []]))
        assert sorted(response.status_code for response in responses) == [200, 409]
        failed = next(response for response in responses if response.status_code == 409)
        assert failed.json()["error"]["code"] == "stale_state"
        saved = owner.get(f"/api/v1/journeys/{identifier}").json()
        assert saved["version"] == 2
        winner = next(response.json() for response in responses if response.status_code == 200)
        assert saved["stops"] == winner["stops"]
        assert saved["total_minutes"] == winner["total_minutes"]
        assert owner.delete("/api/v1/session", headers=ORIGIN).status_code == 200
        with Session(engine) as db:
            assert db.scalar(select(func.count()).select_from(Journey)) == 0
            assert db.scalar(select(func.count()).select_from(JourneyStop)) == 0
