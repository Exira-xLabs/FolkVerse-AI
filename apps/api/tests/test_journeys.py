"""Deterministic journey selection and owned HTTP routes on isolated SQLite.

Synthetic records only: every approval below is an explicitly labelled automated test fixture,
never a real editorial decision. No provider, Postgres or network call is involved.
"""

import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import DateTime, create_engine, delete, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

import folkverse.main as main_module
from folkverse.config import Settings
from folkverse.content import review_record
from folkverse.content_models import (
    Claim,
    ClaimEvidence,
    Exhibit,
    ExhibitRegion,
    Passage,
    Region,
    Source,
)
from folkverse.database import AnonymousSession, Base
from folkverse.guide_index import SnapshotDateTime
from folkverse.journey_api import build_journey_explainer
from folkverse.journey_explanations import ExplanationResult, render_reason
from folkverse.journey_models import Journey, JourneyStop
from folkverse.journey_planner import MAX_STOPS, Candidate, plan, reason_codes, render_notice
from folkverse.main import create_app

ORIGIN = {"Origin": "http://localhost:3000"}
FIXTURE_REVIEWER = "AUTOMATED TEST FIXTURE"


def settings(**changes: Any) -> Settings:
    options: dict[str, Any] = dict(
        _env_file=None,
        app_mode="live",
        database_url="postgresql+psycopg://test:test@localhost/test",
        session_secret="s" * 40,
        allowed_origins=["http://localhost:3000"],
    )
    options.update(changes)
    return Settings(**options)


def _foreign_keys(dbapi: Any, _record: Any) -> None:
    cursor = dbapi.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    engine = create_engine(f"sqlite:///{tmp_path / 'journeys.db'}")
    # Preserve timezone-aware timestamps across the SQLite round trip, like the benchmark path.
    engine.dialect.colspecs = {**engine.dialect.colspecs, DateTime: SnapshotDateTime}
    event.listen(engine, "connect", _foreign_keys)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def app(engine: Engine, monkeypatch: pytest.MonkeyPatch) -> Any:
    """The whole app runs on the isolated SQLite engine, including the session routes."""
    monkeypatch.setattr(main_module, "make_engine", lambda settings: engine)
    application = create_app(settings())
    application.state.engine = engine
    application.state.journey_explainer = None
    application.state.journey_explainer_factory = None
    return application


@pytest.fixture
def client(app: Any) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def approve(db: Session, kind: str, identifier: str) -> None:
    review_record(
        db,
        kind,
        identifier,
        "approved",
        FIXTURE_REVIEWER,
        "Synthetic test record; not a real editorial approval.",
        True,
        True,
    )


def publish(
    db: Session,
    key: str,
    *,
    minutes: int = 3,
    themes: tuple[str, ...] = ("craft",),
    regions: tuple[str, ...] = ("region-a",),
    locales: tuple[str, ...] = ("en", "zh-CN"),
    url: str = "https://example.org/source",
) -> str:
    exhibit_id, source_id = f"exhibit-{key}", f"source-{key}"
    passage_id, claim_id = f"passage-{key}", f"claim-{key}"
    for region_id in regions:
        if db.get(Region, region_id) is None:
            db.add(
                Region(
                    id=region_id,
                    names={"en": region_id, "zh-CN": region_id},
                    approved_geometry_ref=None,
                    status="draft",
                )
            )
    db.add(
        Source(
            id=source_id,
            institution="SYNTHETIC TEST",
            title=f"Source {key}",
            canonical_url=url,
            external_id=source_id,
            fetched_at=datetime(2026, 10, 6),
            raw_hash="synthetic",
            raw_payload="{}",
            rights_basis="Original synthetic test text",
            status="draft",
        )
    )
    db.add(
        Exhibit(
            id=exhibit_id,
            title={locale: f"Exhibit {key} {locale}" for locale in locales},
            summary={locale: f"Summary {key} {locale}" for locale in locales},
            themes=list(themes),
            estimated_minutes=minutes,
            status="draft",
        )
    )
    db.flush()
    db.add(
        Passage(
            id=passage_id,
            source_id=source_id,
            text="Synthetic passage",
            language="en",
            locator="Test entry",
            rights_basis="Original synthetic test text",
            rights_status="pending",
            embedding_version=None,
            status="draft",
        )
    )
    db.add(Claim(id=claim_id, exhibit_id=exhibit_id, text="Synthetic claim", status="draft"))
    db.flush()
    for region_id in regions:
        db.add(
            ExhibitRegion(exhibit_id=exhibit_id, region_id=region_id, geographic_role="practice")
        )
    db.add(ClaimEvidence(claim_id=claim_id, passage_id=passage_id))
    db.flush()
    for region_id in regions:
        approve(db, "region", region_id)
    for kind, identifier in [
        ("source", source_id),
        ("passage", passage_id),
        ("claim", claim_id),
        ("exhibit", exhibit_id),
    ]:
        approve(db, kind, identifier)
    db.commit()
    return exhibit_id


@pytest.fixture
def content(engine: Engine) -> dict[str, str]:
    """Three craft exhibits plus one performance exhibit, all with HTTPS sources."""
    with Session(engine) as db:
        ids = {
            "a": publish(db, "a", minutes=5, regions=("region-a",)),
            "b": publish(db, "b", minutes=5, themes=("performance",), regions=("region-a",)),
            "c": publish(db, "c", minutes=4, regions=("region-b",)),
            "d": publish(db, "d", minutes=20, regions=("region-a",)),
        }
    return ids


def candidate(
    identifier: str,
    minutes: int = 3,
    themes: tuple[str, ...] = ("craft",),
    regions: tuple[str, ...] = ("region-a",),
    locales: tuple[str, ...] = ("en", "zh-CN"),
) -> Candidate:
    return Candidate(
        id=identifier,
        estimated_minutes=minutes,
        themes=themes,
        region_ids=regions,
        locales=locales,
    )


def start_session(client: TestClient) -> str:
    response = client.post("/api/v1/session", headers=ORIGIN)
    assert response.status_code == 200
    return response.json()["session_id"]


def create_journey(client: TestClient, **overrides: Any) -> dict[str, Any]:
    body: dict[str, Any] = {"interests": ["craft"], "locale": "en", "duration_minutes": 30}
    body.update(overrides)
    response = client.post("/api/v1/journeys", json=body, headers=ORIGIN)
    assert response.status_code == 200, response.text
    return response.json()


# --------------------------------------------------------------------------------------------
# Pure planner
# --------------------------------------------------------------------------------------------


def test_plan_uses_stored_minutes_and_never_exceeds_the_request() -> None:
    result = plan(
        [candidate("a", 5), candidate("b", 7), candidate("c", 11)],
        interests=["craft"],
        locale="en",
        duration_minutes=12,
    )
    minutes = {
        selection.candidate.id: selection.candidate.estimated_minutes
        for selection in result.selections
    }
    assert result.total_minutes == sum(minutes.values()) <= 12
    assert result.total_minutes == 12  # 5 + 7 rather than the 11-minute stop
    assert all(value > 0 for value in minutes.values())
    assert result.notice_codes == ()


def test_plan_is_stable_under_input_order_and_deduplicates_candidates() -> None:
    corpus = [candidate("a", 3), candidate("b", 4), candidate("c", 3), candidate("d", 6)]
    expected = plan(corpus, interests=["craft"], locale="en", duration_minutes=10)
    for order in ([3, 1, 0, 2], [2, 0, 3, 1], [1, 3, 2, 0]):
        shuffled = [corpus[index] for index in order]
        assert plan(shuffled, interests=["craft"], locale="en", duration_minutes=10) == expected
    duplicated = plan(
        [candidate("a", 4), candidate("a", 3), candidate("a", 9)],
        interests=["craft"],
        locale="en",
        duration_minutes=10,
    )
    assert [selection.candidate.id for selection in duplicated.selections] == ["a"]
    assert duplicated.total_minutes == 3
    invalid = plan(
        [candidate("zero", 0), candidate("fine", 4)],
        interests=["craft"],
        locale="en",
        duration_minutes=10,
    )
    assert [selection.candidate.id for selection in invalid.selections] == ["fine"]


def test_plan_enforces_locale_region_and_interest_eligibility() -> None:
    corpus = [
        candidate("en-only", 5, locales=("en",)),
        candidate("zh-only", 5, locales=("zh-CN",)),
        candidate("other-region", 5, regions=("region-z",)),
        candidate("other-theme", 5, themes=("music",)),
    ]
    english = plan(
        corpus, interests=["craft"], locale="en", duration_minutes=20, region_id="region-a"
    )
    assert [selection.candidate.id for selection in english.selections] == ["en-only"]
    chinese = plan(
        corpus, interests=["craft"], locale="zh-CN", duration_minutes=20, region_id="region-a"
    )
    assert [selection.candidate.id for selection in chinese.selections] == ["zh-only"]
    wide = plan(corpus, interests=["craft"], locale="en", duration_minutes=20)
    assert [selection.candidate.id for selection in wide.selections] == [
        "en-only",
        "other-region",
    ]
    no_interest = plan(corpus, interests=["unknown"], locale="en", duration_minutes=20)
    assert no_interest.selections == ()
    assert no_interest.notice_codes == ("no_candidates",)


def test_plan_prefers_explicit_novelty_and_spreads_themes() -> None:
    corpus = [
        candidate("craft-1", 4, themes=("craft",)),
        candidate("craft-2", 4, themes=("craft",)),
        candidate("music-1", 4, themes=("music",)),
        candidate("history-1", 4, themes=("history",)),
    ]
    diverse = plan(
        corpus, interests=["craft", "music", "history"], locale="en", duration_minutes=12
    )
    assert len(diverse.selections) == 3
    themes = {theme for selection in diverse.selections for theme in selection.candidate.themes}
    assert len(themes) == 3
    fresh = plan(
        [candidate("seen", 4), candidate("fresh", 4)],
        interests=["craft"],
        locale="en",
        duration_minutes=4,
        novelty_exhibit_ids=["seen"],
    )
    assert [selection.candidate.id for selection in fresh.selections] == ["fresh"]
    # No novelty list supplied means no freshness claim can be made.
    repeat = plan(
        [candidate("seen", 4), candidate("fresh", 4)],
        interests=["craft"],
        locale="en",
        duration_minutes=4,
    )
    assert "new_discovery" not in dict(
        (selection.candidate.id, selection.codes) for selection in repeat.selections
    )["fresh"]
    assert dict((s.candidate.id, s.codes) for s in repeat.selections)["fresh"] == (
        "theme_match",
        "time_fit",
    )


def test_plan_start_exhibit_is_first_or_explained_in_a_notice() -> None:
    corpus = [
        candidate("start", 5),
        candidate("other", 5),
        candidate("music", 5, themes=("music",)),
    ]
    first = plan(
        corpus,
        interests=["craft"],
        locale="en",
        duration_minutes=20,
        start_exhibit_id="start",
    )
    assert first.selections[0].candidate.id == "start"
    assert "starting_exhibit" in first.selections[0].codes
    filtered = plan(
        [candidate("music", 5, themes=("music",)), candidate("craft", 5)],
        interests=["craft"],
        locale="en",
        duration_minutes=20,
        start_exhibit_id="music",
    )
    assert filtered.notice_codes == ("start_filtered", "partial_fill")
    assert "music" not in [selection.candidate.id for selection in filtered.selections]
    too_long = plan(
        [candidate("start", 30), candidate("other", 5)],
        interests=["craft"],
        locale="en",
        duration_minutes=10,
        start_exhibit_id="start",
    )
    assert too_long.notice_codes == ("start_too_long", "partial_fill")
    assert [selection.candidate.id for selection in too_long.selections] == ["other"]
    ineligible = plan(
        [candidate("start", 5, locales=("en",))],
        interests=["craft"],
        locale="zh-CN",
        duration_minutes=10,
        start_exhibit_id="start",
    )
    assert ineligible.notice_codes == ("start_ineligible", "no_candidates")


def test_plan_empty_too_small_and_capped_corpora_are_explicit() -> None:
    empty = plan([], interests=["craft"], locale="en", duration_minutes=10)
    assert empty.selections == () and empty.notice_codes == ("no_candidates",)
    too_small = plan([candidate("long", 30)], interests=["craft"], locale="en", duration_minutes=10)
    assert too_small.notice_codes == ("no_fit",)
    partial = plan([candidate("short", 2)], interests=["craft"], locale="en", duration_minutes=10)
    assert partial.total_minutes == 2 and partial.notice_codes == ("partial_fill",)
    assert "cover 2 of the 10 minutes" in (partial.notice or "")
    capped = plan(
        [candidate(f"e{index:02d}", 1) for index in range(40)],
        interests=["craft"],
        locale="en",
        duration_minutes=60,
        start_exhibit_id="e00",
    )
    assert len(capped.selections) == MAX_STOPS
    assert capped.selections[0].candidate.id == "e00"
    assert "cap" in capped.notice_codes
    stopped_ids = {selection.candidate.id for selection in capped.selections}
    assert len(capped.selections) == len(stopped_ids)


def test_reason_codes_track_interest_novelty_and_start() -> None:
    seen = {"seen"}  # novelty IDs are supplied explicitly by the client, never inferred
    assert reason_codes(
        candidate("start"),
        interests={"craft"},
        novelty_exhibit_ids=set(),
        start_exhibit_id="start",
    ) == ("time_fit", "starting_exhibit")
    assert reason_codes(
        candidate("match"), interests={"craft"}, novelty_exhibit_ids=set(), start_exhibit_id=None
    ) == ("theme_match", "time_fit")
    assert reason_codes(
        candidate("fresh", themes=("music",)),
        interests={"craft"},
        novelty_exhibit_ids=seen,
        start_exhibit_id=None,
    ) == ("time_fit", "new_discovery")
    assert reason_codes(
        candidate("seen", themes=("music",)),
        interests={"craft"},
        novelty_exhibit_ids=seen,
        start_exhibit_id=None,
    ) == ("time_fit", "collection_discovery")
    assert render_notice(("no_candidates",), "zh-CN", duration_minutes=10) is not None


# --------------------------------------------------------------------------------------------
# HTTP boundary
# --------------------------------------------------------------------------------------------


def test_create_returns_resolved_route_with_sources_and_reloads(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    session_id = start_session(client)
    body = create_journey(client, duration_minutes=14, novelty_exhibit_ids=[content["d"]])
    assert body["id"].startswith("jrn_")
    assert body["interests"] == ["craft"] and body["duration_minutes"] == 14
    assert body["region_id"] is None and body["version"] == 1
    assert body["explanation_status"] == "deterministic"
    assert body["novelty_exhibit_ids"] == [content["d"]]
    assert body["total_minutes"] <= 14 and body["total_minutes"] == sum(
        stop["estimated_minutes"] for stop in body["stops"]
    )
    assert body["stops"], "the fixture corpus has matching published exhibits"
    for stop in body["stops"]:
        assert stop["title"] and stop["summary"] and stop["reason"]
        assert stop["estimated_minutes"] > 0 and stop["region_ids"] and stop["themes"]
        assert stop["sources"], "no stop may appear without an inspectable source"
        assert all(source["canonical_url"].startswith("https://") for source in stop["sources"])

    detail = client.get(f"/api/v1/journeys/{body['id']}")
    assert detail.status_code == 200
    assert detail.json() == body
    listed = client.get("/api/v1/journeys").json()
    assert [item["id"] for item in listed["items"]] == [body["id"]]

    localized = client.get(
        f"/api/v1/journeys/{body['id']}", params={"locale": "zh-CN"}
    ).json()
    assert localized["locale"] == "zh-CN"
    assert localized["stops"][0]["title"] == f"Exhibit {body['stops'][0]['exhibit_id'][-1]} zh-CN"
    assert localized["interests"] == body["interests"]
    with Session(engine) as db:
        row = db.get(Journey, body["id"])
        assert row is not None and row.locale == "en" and row.owner_session == session_id


def test_create_requires_a_session_and_rejects_loose_or_unknown_input(
    client: TestClient, content: dict[str, str]
) -> None:
    body = {"interests": ["craft"], "locale": "en", "duration_minutes": 10}
    assert client.post("/api/v1/journeys", json=body, headers=ORIGIN).status_code == 401
    start_session(client)
    for invalid in [
        body | {"duration_minutes": 4},
        body | {"duration_minutes": 61},
        body | {"duration_minutes": 10.5},
        body | {"owner_session": "someone-else"},
        body | {"interests": [f"i{index}" for index in range(9)]},
        body | {"interests": ["  "]},
        body | {"locale": "fr"},
    ]:
        response = client.post("/api/v1/journeys", json=invalid, headers=ORIGIN)
        assert response.status_code == 422, invalid
        assert response.json()["error"]["code"] == "invalid_input"
    assert client.post("/api/v1/journeys", json=body).status_code == 403  # origin enforced


def test_region_without_published_exhibits_is_an_empty_route(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    with Session(engine) as db:
        db.add(
            Region(
                id="region-empty",
                names={"en": "Empty", "zh-CN": "空"},
                approved_geometry_ref=None,
                status="draft",
            )
        )
        db.commit()
    start_session(client)
    empty = create_journey(client, region_id="region-empty")
    assert empty["stops"] == [] and empty["total_minutes"] == 0
    assert empty["notice"] and "No published exhibit" in empty["notice"]
    unknown = client.post(
        "/api/v1/journeys",
        json={
            "interests": ["craft"],
            "locale": "en",
            "duration_minutes": 10,
            "region_id": "region-does-not-exist",
        },
        headers=ORIGIN,
    )
    assert unknown.status_code == 422 and unknown.json()["error"]["code"] == "unknown_region"


def test_patch_reorders_removes_and_stays_within_one_session(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    session_id = start_session(client)
    journey = create_journey(client, duration_minutes=10)
    ordered = [stop["exhibit_id"] for stop in journey["stops"]]
    assert len(ordered) >= 2

    reordered = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": list(reversed(ordered)), "expected_version": 1},
        headers=ORIGIN,
    )
    assert reordered.status_code == 200
    assert [stop["exhibit_id"] for stop in reordered.json()["stops"]] == list(reversed(ordered))
    assert reordered.json()["version"] == 2
    assert reordered.json()["total_minutes"] == journey["total_minutes"]

    removed = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": ordered[:1]},
        headers=ORIGIN,
    )
    assert [stop["exhibit_id"] for stop in removed.json()["stops"]] == ordered[:1]
    assert removed.json()["version"] == 3

    emptied = client.patch(
        f"/api/v1/journeys/{journey['id']}", json={"ordered_exhibit_ids": []}, headers=ORIGIN
    )
    assert emptied.status_code == 200
    assert emptied.json()["stops"] == [] and emptied.json()["total_minutes"] == 0

    # A body without the list must never silently wipe the route.
    for incomplete in ({}, {"expected_version": 1}, {"ordered": []}):
        refused = client.patch(
            f"/api/v1/journeys/{journey['id']}", json=incomplete, headers=ORIGIN
        )
        assert refused.status_code == 422, incomplete
    assert client.get(f"/api/v1/journeys/{journey['id']}").json()["version"] == 4

    client.cookies.clear()
    start_session(client)
    assert client.get(f"/api/v1/journeys/{journey['id']}").status_code == 403
    blocked = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": ordered},
        headers=ORIGIN,
    )
    assert blocked.status_code == 403 and blocked.json()["error"]["code"] == "ownership_denied"
    assert client.get("/api/v1/journeys/nope").status_code == 404
    assert (
        client.patch(
            "/api/v1/journeys/nope", json={"ordered_exhibit_ids": []}, headers=ORIGIN
        ).status_code
        == 404
    )
    with Session(engine) as db:
        row = db.get(Journey, journey["id"])
        assert row is not None and row.owner_session == session_id and row.total_minutes == 0


def test_patch_rejects_duplicates_unpublished_and_over_time(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    journey = create_journey(client, duration_minutes=10)
    ordered = [stop["exhibit_id"] for stop in journey["stops"]]
    assert ordered

    duplicate = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [ordered[0], ordered[0]]},
        headers=ORIGIN,
    )
    assert duplicate.status_code == 422 and duplicate.json()["error"]["code"] == "duplicate_exhibit"

    unknown = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": ["exhibit-missing"]},
        headers=ORIGIN,
    )
    assert unknown.status_code == 422 and unknown.json()["error"]["code"] == "unknown_exhibit"

    over_time = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [content["d"], content["a"], content["c"]]},
        headers=ORIGIN,
    )
    assert over_time.status_code == 422 and over_time.json()["error"]["code"] == "exceeds_duration"

    stale = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": ordered, "expected_version": 7},
        headers=ORIGIN,
    )
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "stale_state"

    assert (
        client.patch(
            f"/api/v1/journeys/{journey['id']}",
            json={"ordered_exhibit_ids": ordered, "expected_version": True},
            headers=ORIGIN,
        ).status_code
        == 422
    )

    # Withdrawing a published exhibit makes it unusable for a save, and the stored route keeps
    # working until it is read again.
    with Session(engine) as db:
        approve_row = db.get(Exhibit, content["a"])
        assert approve_row is not None
        review_record(
            db,
            "exhibit",
            content["a"],
            "withdrawn",
            FIXTURE_REVIEWER,
            "Synthetic withdrawal during the test.",
            True,
        )
        db.commit()
    withdrawn = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [content["a"]]},
        headers=ORIGIN,
    )
    assert withdrawn.status_code == 422 and withdrawn.json()["error"]["code"] == "unknown_exhibit"


def test_get_prunes_withdrawn_stops_with_an_explicit_notice(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    journey = create_journey(client, duration_minutes=10)
    ordered = [stop["exhibit_id"] for stop in journey["stops"]]
    assert len(ordered) >= 2

    with Session(engine) as db:
        source_id = db.scalars(
            select(Source.id)
            .join(Passage, Passage.source_id == Source.id)
            .where(Passage.id == f"passage-{ordered[0].removeprefix('exhibit-')}")
        ).one()
        review_record(
            db,
            "source",
            source_id,
            "withdrawn",
            FIXTURE_REVIEWER,
            "Synthetic withdrawal during the test.",
            True,
        )
        db.commit()

    pruned = client.get(f"/api/v1/journeys/{journey['id']}").json()
    assert ordered[0] not in [stop["exhibit_id"] for stop in pruned["stops"]]
    assert pruned["notice"] and "no longer published" in pruned["notice"]
    assert pruned["total_minutes"] == sum(
        stop["estimated_minutes"] for stop in pruned["stops"]
    )

    # Approval is restored; the read-time projection is deliberately not persisted, so the stop
    # reappears. This tradeoff is documented on the module.
    with Session(engine) as db:
        approve(db, "source", source_id)
        db.commit()
    restored = client.get(f"/api/v1/journeys/{journey['id']}").json()
    assert [stop["exhibit_id"] for stop in restored["stops"]] == ordered


def test_stop_without_https_source_is_never_selected(engine: Engine, client: TestClient) -> None:
    with Session(engine) as db:
        publish(db, "http", url="http://example.org/insecure")
    start_session(client)
    insecure = create_journey(client, duration_minutes=30)
    assert insecure["stops"] == []
    assert insecure["notice"] and "No published exhibit" in insecure["notice"]


def test_session_expiry_and_deletion_remove_access_and_rows(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    expired_id = start_session(client)
    journey = create_journey(client, duration_minutes=10)
    with Session(engine) as db:
        row = db.get(AnonymousSession, expired_id)
        assert row is not None
        row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        db.commit()
    assert client.get("/api/v1/journeys").status_code == 401
    assert client.get(f"/api/v1/journeys/{journey['id']}").status_code == 401
    assert (
        client.patch(
            f"/api/v1/journeys/{journey['id']}",
            json={"ordered_exhibit_ids": []},
            headers=ORIGIN,
        ).status_code
        == 401
    )
    with Session(engine) as db:
        assert db.get(Journey, journey["id"]) is not None  # an expired session keeps its rows

    client.cookies.clear()
    active_id = start_session(client)
    doomed = create_journey(client, duration_minutes=10)
    assert client.delete("/api/v1/session", headers=ORIGIN).status_code == 200
    with Session(engine) as db:
        assert db.get(AnonymousSession, active_id) is None
        assert db.get(Journey, doomed["id"]) is None
        assert not list(
            db.scalars(select(JourneyStop).where(JourneyStop.journey_id == doomed["id"]))
        )
        assert db.get(Journey, journey["id"]) is not None


def test_journey_body_limit_is_enforced_before_parsing(client: TestClient) -> None:
    oversized = b'"' + b"x" * 20000 + b'"'
    response = client.post(
        "/api/v1/journeys",
        content=oversized,
        headers={**ORIGIN, "Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "context_too_large"
    assert "xxxx" not in response.text


# --------------------------------------------------------------------------------------------
# Optional explanation upgrade
# --------------------------------------------------------------------------------------------


class FakeExplainer:
    def __init__(
        self,
        *,
        status: str = "generated",
        codes: dict[str, list[str]] | None = None,
        on_call: Any = None,
    ) -> None:
        self.status, self.codes, self.on_call = status, codes, on_call
        self.calls: list[dict[str, Any]] = []

    async def explain(
        self,
        stops: list[dict[str, Any]],
        locale: str,
        interests: list[str],
        actor_id: str,
        corpus_signature: str,
    ) -> ExplanationResult:
        self.calls.append(
            {
                "stops": stops,
                "locale": locale,
                "interests": interests,
                "actor_id": actor_id,
                "signature": corpus_signature,
            }
        )
        if self.on_call is not None:
            self.on_call()
        if self.status != "generated":
            return ExplanationResult(status="unavailable")
        codes = self.codes or {stop["exhibit_id"]: ["time_fit"] for stop in stops}
        return ExplanationResult(
            status="generated", reasons={key: "server text" for key in codes}, codes=codes
        )


def test_explainer_upgrades_codes_with_the_server_rendered_text(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    session_id = start_session(client)
    client.app.state.journey_explainer = FakeExplainer()
    journey = create_journey(client, duration_minutes=10)
    explainer = client.app.state.journey_explainer
    assert journey["explanation_status"] == "generated"
    assert explainer.calls and explainer.calls[0]["actor_id"] == session_id
    assert explainer.calls[0]["locale"] == "en"
    assert explainer.calls[0]["signature"] and len(explainer.calls[0]["signature"]) == 64
    for stop in explainer.calls[0]["stops"]:
        assert stop["allowed_reason_codes"]
        assert set(stop["allowed_reason_codes"]) <= {
            "theme_match",
            "time_fit",
            "starting_exhibit",
            "new_discovery",
            "collection_discovery",
        }
        assert stop["fallback_reason"]
    for stop in journey["stops"]:
        assert stop["reason"] == "This stop fits the amount of time you set for the route."
    reloaded = client.get(f"/api/v1/journeys/{journey['id']}").json()
    assert reloaded["explanation_status"] == "generated"
    assert reloaded["stops"] == journey["stops"]


def test_explainer_failure_and_unvalidated_codes_fall_back_safely(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    client.app.state.journey_explainer = FakeExplainer(status="unavailable")
    unavailable = create_journey(client, duration_minutes=10)
    assert unavailable["explanation_status"] == "unavailable"
    assert all(stop["reason"] for stop in unavailable["stops"])

    client.app.state.journey_explainer = FakeExplainer(codes={"made-up": ["time_fit"]})
    invalid = create_journey(client, duration_minutes=10)
    assert invalid["explanation_status"] == "unavailable"
    assert all(stop["reason"] for stop in invalid["stops"])


def test_revalidation_after_the_provider_call_never_publishes_stale_labels(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)

    def withdraw() -> None:
        with Session(engine) as db:
            review_record(
                db,
                "exhibit",
                content["a"],
                "withdrawn",
                FIXTURE_REVIEWER,
                "Synthetic withdrawal during the provider call.",
                True,
            )
            db.commit()

    client.app.state.journey_explainer = FakeExplainer(on_call=withdraw)
    journey = create_journey(client, duration_minutes=10)
    assert journey["explanation_status"] == "unavailable"
    assert content["a"] not in [stop["exhibit_id"] for stop in journey["stops"]]
    assert journey["notice"] and "no longer published" in journey["notice"]

    # A session deleted while the provider is thinking must surface as 401, not as a response
    # carrying labels computed for a session that no longer exists.
    client.cookies.clear()
    doomed_id = start_session(client)

    def delete_current() -> None:
        with Session(engine) as db:
            row = db.get(AnonymousSession, doomed_id)
            assert row is not None
            db.delete(row)
            db.commit()

    client.app.state.journey_explainer = FakeExplainer(on_call=delete_current)
    expired = client.post(
        "/api/v1/journeys",
        json={"interests": ["craft"], "locale": "en", "duration_minutes": 10},
        headers=ORIGIN,
    )
    assert expired.status_code == 401
    assert expired.json()["error"]["code"] in {"session_required", "session_expired"}


def test_factory_requires_a_ready_provider() -> None:
    def app_with(**changes: Any) -> SimpleNamespace:
        return SimpleNamespace(
            state=SimpleNamespace(
                settings=settings(**changes),
                guide_gateway=object(),
                journey_explainer=None,
            )
        )

    assert build_journey_explainer(app_with(app_mode="demo")) is None
    assert build_journey_explainer(app_with()) is None
    assert build_journey_explainer(app_with(guide_provider="ollama")) is None
    ollama = app_with(
        guide_provider="ollama", ollama_api_key="SYNTHETIC", ollama_daily_request_limit=3
    )
    assert build_journey_explainer(ollama) is not None


def test_journey_rows_are_bounded_and_json_safe(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    journey = create_journey(client, duration_minutes=30)
    payload = json.dumps(journey, ensure_ascii=False)
    assert "jrn_" in payload
    with Session(engine) as db:
        stops = list(
            db.scalars(select(JourneyStop).where(JourneyStop.journey_id == journey["id"]))
        )
        assert len(stops) <= MAX_STOPS
        assert [stop.position for stop in stops] == list(range(len(stops)))


# --------------------------------------------------------------------------------------------
# Regressions: current-truth notices, PATCH criteria and concurrent provider writes
# --------------------------------------------------------------------------------------------


def test_start_too_long_notice_is_rederived_from_current_content(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    journey = create_journey(client, duration_minutes=10, start_exhibit_id=content["d"])
    assert content["d"] not in [stop["exhibit_id"] for stop in journey["stops"]]
    assert "needs 20 minutes" in (journey["notice"] or "")

    with Session(engine) as db:
        review_record(
            db,
            "exhibit",
            content["d"],
            "withdrawn",
            FIXTURE_REVIEWER,
            "Synthetic withdrawal during the test.",
            True,
        )
        db.commit()
    gone = client.get(f"/api/v1/journeys/{journey['id']}").json()
    notice = gone["notice"] or ""
    assert "needs 0 minutes" not in notice
    assert "longer than" not in notice
    assert "not published for this language and region" in notice

    # The exhibit is restored and now fits the route: the stale claim must disappear entirely.
    with Session(engine) as db:
        row = db.get(Exhibit, content["d"])
        assert row is not None
        row.estimated_minutes = 4
        db.flush()
        approve(db, "exhibit", content["d"])
        db.commit()
    fits = client.get(f"/api/v1/journeys/{journey['id']}").json()
    assert "starting exhibit" not in (fits["notice"] or "")
    assert "longer than" not in (fits["notice"] or "")
    assert "needs " not in (fits["notice"] or "")


def test_patch_rejects_stops_outside_stored_region_and_interests(
    client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    journey = create_journey(client, duration_minutes=30, region_id="region-a")
    assert journey["region_id"] == "region-a"

    outside_region = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [content["c"]]},
        headers=ORIGIN,
    )
    assert outside_region.status_code == 422
    assert outside_region.json()["error"]["code"] == "invalid_input"

    outside_theme = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [content["b"]]},
        headers=ORIGIN,
    )
    assert outside_theme.status_code == 422
    assert outside_theme.json()["error"]["code"] == "invalid_input"

    kept = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [content["a"]]},
        headers=ORIGIN,
    )
    assert kept.status_code == 200
    assert [stop["exhibit_id"] for stop in kept.json()["stops"]] == [content["a"]]

    open_route = create_journey(client, interests=[], duration_minutes=30)
    accepted = client.patch(
        f"/api/v1/journeys/{open_route['id']}",
        json={"ordered_exhibit_ids": [content["b"], content["c"]]},
        headers=ORIGIN,
    )
    assert accepted.status_code == 200
    assert {stop["exhibit_id"] for stop in accepted.json()["stops"]} == {
        content["b"],
        content["c"],
    }


def test_patch_requires_stops_to_render_in_the_display_locale(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    with Session(engine) as db:
        english_only = publish(db, "english-only", minutes=3, locales=("en",))
    start_session(client)
    journey = create_journey(client, duration_minutes=10)
    assert english_only not in [stop["exhibit_id"] for stop in journey["stops"]]

    mismatch = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [english_only]},
        params={"locale": "zh-CN"},
        headers=ORIGIN,
    )
    assert mismatch.status_code == 422
    assert mismatch.json()["error"]["code"] == "invalid_input"

    accepted = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [english_only]},
        headers=ORIGIN,
    )
    assert accepted.status_code == 200
    assert [stop["exhibit_id"] for stop in accepted.json()["stops"]] == [english_only]

    chinese = client.get(
        f"/api/v1/journeys/{journey['id']}", params={"locale": "zh-CN"}
    ).json()
    assert chinese["stops"] == []
    assert chinese["locale"] == "zh-CN"
    assert chinese["notice"] and "不可用" in chinese["notice"]


def test_composition_change_recomputes_deterministic_reasons(
    client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    client.app.state.journey_explainer = FakeExplainer()
    journey = create_journey(client, duration_minutes=10)
    assert journey["explanation_status"] == "generated"
    model_text = journey["stops"][0]["reason"]
    ordered = [stop["exhibit_id"] for stop in journey["stops"]]
    assert len(ordered) == 2

    reordered = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": list(reversed(ordered))},
        headers=ORIGIN,
    ).json()
    assert reordered["explanation_status"] == "generated"
    assert all(stop["reason"] == model_text for stop in reordered["stops"])

    trimmed = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": ordered[:1]},
        headers=ORIGIN,
    ).json()
    assert trimmed["explanation_status"] == "deterministic"
    stop = trimmed["stops"][0]
    expected = render_reason(
        reason_codes(
            candidate(stop["exhibit_id"], stop["estimated_minutes"], tuple(stop["themes"])),
            interests={"craft"},
            novelty_exhibit_ids=set(),
            start_exhibit_id=None,
        ),
        "en",
    )
    assert stop["reason"] == expected
    assert stop["reason"] != model_text


def test_start_exhibit_over_http_is_first_reorderable_and_removable(
    client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)
    journey = create_journey(client, duration_minutes=10, start_exhibit_id=content["a"])
    assert journey["stops"][0]["exhibit_id"] == content["a"]
    assert journey["stops"][0]["reason"] == render_reason(("time_fit", "starting_exhibit"), "en")
    others = [stop["exhibit_id"] for stop in journey["stops"][1:]]
    assert others

    pushed_back = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [*others, content["a"]]},
        headers=ORIGIN,
    ).json()
    assert pushed_back["stops"][-1]["exhibit_id"] == content["a"]
    assert pushed_back["stops"][-1]["reason"] == render_reason(("time_fit",), "en")

    first_again = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": [content["a"], *others]},
        headers=ORIGIN,
    ).json()
    assert first_again["stops"][0]["exhibit_id"] == content["a"]
    assert first_again["stops"][0]["reason"] == render_reason(
        ("time_fit", "starting_exhibit"), "en"
    )

    removed = client.patch(
        f"/api/v1/journeys/{journey['id']}",
        json={"ordered_exhibit_ids": others},
        headers=ORIGIN,
    ).json()
    assert content["a"] not in [stop["exhibit_id"] for stop in removed["stops"]]
    assert all("starting point" not in stop["reason"] for stop in removed["stops"])
    with Session(client.app.state.engine) as db:
        row = db.get(Journey, journey["id"])
        assert row is not None and row.start_exhibit_id == content["a"]

    # A declared start that contradicts the interests is left out with an explicit notice, not an
    # error, and the stored preference is kept for the next regeneration.
    filtered = create_journey(client, duration_minutes=10, start_exhibit_id=content["b"])
    assert content["b"] not in [stop["exhibit_id"] for stop in filtered["stops"]]
    assert "does not match the interests" in (filtered["notice"] or "")
    with Session(client.app.state.engine) as db:
        row = db.get(Journey, filtered["id"])
        assert row is not None and row.start_exhibit_id == content["b"]


def test_concurrent_patch_during_explanation_is_preserved(
    engine: Engine, client: TestClient, content: dict[str, str]
) -> None:
    start_session(client)

    def concurrent_edit() -> None:
        with Session(engine) as db:
            row = db.scalars(select(Journey)).one()
            db.execute(delete(JourneyStop).where(JourneyStop.journey_id == row.id))
            db.add(
                JourneyStop(
                    journey_id=row.id,
                    position=0,
                    exhibit_id=content["c"],
                    reason_codes=["theme_match", "time_fit"],
                )
            )
            row.version += 1
            row.total_minutes = 4
            row.updated_at = datetime.now(UTC)
            row.explanation_status = "deterministic"
            db.commit()

    client.app.state.journey_explainer = FakeExplainer(on_call=concurrent_edit)
    journey = create_journey(client, duration_minutes=10)
    assert journey["version"] == 2
    assert [stop["exhibit_id"] for stop in journey["stops"]] == [content["c"]]
    assert journey["total_minutes"] == 4
    assert journey["explanation_status"] == "deterministic"
    assert journey["stops"][0]["reason"] == render_reason(("theme_match", "time_fit"), "en")
    assert journey["stops"][0]["reason"] != render_reason(("time_fit",), "en")


def test_journey_list_locale_order_and_limit(client: TestClient, content: dict[str, str]) -> None:
    start_session(client)
    older = create_journey(client, duration_minutes=10)
    newer = create_journey(client, duration_minutes=12, interests=["performance"])

    listed = client.get("/api/v1/journeys").json()["items"]
    assert [item["id"] for item in listed] == [newer["id"], older["id"]]

    touched = client.patch(
        f"/api/v1/journeys/{older['id']}",
        json={"ordered_exhibit_ids": [stop["exhibit_id"] for stop in older["stops"]]},
        headers=ORIGIN,
    )
    assert touched.status_code == 200 and touched.json()["version"] == 2
    after = client.get("/api/v1/journeys").json()["items"]
    assert [item["id"] for item in after] == [older["id"], newer["id"]]

    limited = client.get("/api/v1/journeys", params={"limit": 1}).json()["items"]
    assert [item["id"] for item in limited] == [older["id"]]
    chinese = client.get("/api/v1/journeys", params={"locale": "zh-CN"}).json()["items"]
    assert all(item["locale"] == "zh-CN" for item in chinese)
    assert all(stop["title"].endswith("zh-CN") for item in chinese for stop in item["stops"])
    assert client.get("/api/v1/journeys", params={"limit": 0}).status_code == 422
    assert client.get("/api/v1/journeys", params={"limit": 21}).status_code == 422


def test_journey_patch_body_limit_is_enforced(client: TestClient, content: dict[str, str]) -> None:
    start_session(client)
    oversized = b'"' + b"x" * 20000 + b'"'
    response = client.patch(
        "/api/v1/journeys/jrn_oversized",
        content=oversized,
        headers={**ORIGIN, "Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "context_too_large"
    assert "xxxx" not in response.text
