"""Publication invariants against PostgreSQL; all test records roll back."""

import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from folkverse import content, met_import
from folkverse.config import Settings
from folkverse.content import approved, counts, published_exhibits, review_record
from folkverse.content_models import (
    Artifact,
    Claim,
    ClaimEvidence,
    Exhibit,
    ExhibitRegion,
    Media,
    Passage,
    Region,
    Source,
)
from folkverse.database import make_engine
from folkverse.main import create_app


@pytest.fixture
def db() -> Iterator[Session]:
    engine = make_engine(Settings())
    with engine.connect() as connection:
        transaction = connection.begin()
        with Session(connection) as session:
            yield session
        transaction.rollback()
    engine.dispose()


def approve(db: Session, kind: str, identifier: str) -> None:
    review_record(
        db,
        kind,
        identifier,
        "approved",
        "AUTOMATED TEST FIXTURE",
        "Isolated synthetic record; not a real editorial approval.",
        True,
        True,
    )
    db.expire_all()  # Check persisted representations, including timezone normalization.


def candidate(db: Session, suffix: str = "a") -> tuple[Exhibit, Source, Passage]:
    eid, sid, pid, rid, cid = [f"test-{kind}-{suffix}" for kind in ["e", "s", "p", "r", "c"]]
    region = Region(
        id=rid,
        names={"en": "Test city", "zh-CN": "测试城市"},
        approved_geometry_ref=None,
        status="draft",
    )
    source = Source(
        id=sid,
        institution="TEST",
        external_id=sid,
        title="Test source",
        canonical_url="https://example.org/test",
        fetched_at=datetime.now(UTC),
        raw_payload="{}",
        raw_hash=hashlib.sha256(b"{}").hexdigest(),
        rights_basis="Original synthetic test",
        status="draft",
    )
    exhibit = Exhibit(
        id=eid,
        title={"en": "Test theatre", "zh-CN": "测试戏剧"},
        summary={"en": "A synthetic record", "zh-CN": "测试记录"},
        themes=["performance"],
        estimated_minutes=3,
        status="draft",
    )
    db.add_all([region, source, exhibit])
    db.flush()
    passage = Passage(
        id=pid,
        source_id=sid,
        text="A synthetic record",
        language="en",
        locator="Test",
        rights_basis="Original synthetic test",
        rights_status="pending",
        embedding_version=None,
        status="draft",
    )
    claim = Claim(id=cid, exhibit_id=eid, text=passage.text, status="draft")
    db.add_all([passage, claim])
    db.flush()
    db.add_all(
        [
            ExhibitRegion(exhibit_id=eid, region_id=rid, geographic_role="practice"),
            ClaimEvidence(claim_id=cid, passage_id=pid),
        ]
    )
    db.flush()
    return exhibit, source, passage


def publish(db: Session, suffix: str = "a") -> tuple[Exhibit, Source, Passage]:
    rows = candidate(db, suffix)
    for kind, key in [
        ("region", "r"),
        ("source", "s"),
        ("passage", "p"),
        ("claim", "c"),
        ("exhibit", "e"),
    ]:
        approve(db, kind, f"test-{key}-{suffix}")
    return rows


def test_human_review_and_rights_are_required(db: Session) -> None:
    exhibit, _, passage = candidate(db)
    with pytest.raises(ValueError, match="named human"):
        review_record(db, "exhibit", exhibit.id, "approved", "", "", False)
    with pytest.raises(ValueError, match="Review all"):
        approve(db, "exhibit", exhibit.id)
    with pytest.raises(ValueError, match="clear-rights"):
        review_record(db, "passage", passage.id, "approved", "TEST", "Test", True)
    assert not approved(db, exhibit)


def test_withdrawal_and_changed_content_fail_closed(db: Session) -> None:
    exhibit, source, passage = publish(db)
    assert exhibit.id in [e.id for e in published_exhibits(db)]
    passage.embedding_version = "synthetic-vector-v1"
    db.flush()
    review_record(db, "source", source.id, "withdrawn", "TEST", "Test withdrawal", True)
    assert passage.embedding_version is None
    assert exhibit.id not in [e.id for e in published_exhibits(db)]
    approve(db, "source", source.id)
    assert exhibit.id in [e.id for e in published_exhibits(db)]
    exhibit.summary = {"en": "Unreviewed mutation", "zh-CN": "未经审核"}
    db.flush()
    assert exhibit.id not in [e.id for e in published_exhibits(db)]


@pytest.mark.parametrize("dependency", ["region", "passage", "claim", "exhibit"])
def test_each_dependency_withdrawal_removes_exhibit(db: Session, dependency: str) -> None:
    exhibit, _, _ = publish(db)
    key = {"region": "r", "passage": "p", "claim": "c", "exhibit": "e"}[dependency]
    review_record(db, dependency, f"test-{key}-a", "withdrawn", "TEST", "Test", True)
    assert exhibit.id not in [e.id for e in published_exhibits(db)]


def test_api_pagination_filters_drafts_and_immediate_withdrawal(db: Session) -> None:
    exhibit, source, _ = publish(db)
    candidate(db, "draft")
    publish(db, "b")
    app = create_app()
    with TestClient(app) as client:
        engine = app.state.engine
        app.state.engine = db.get_bind()
        response = client.get("/api/v1/exhibits", params={"q": "Test theatre", "limit": 1})
        assert response.headers["cache-control"] == "no-store"
        body = response.json()
        assert body["total"] == 2 and len(body["items"]) == 1 and body["next_cursor"]
        after = client.get(
            "/api/v1/exhibits",
            params={"q": "Test theatre", "limit": 1, "cursor": body["next_cursor"]},
        ).json()
        assert after["items"][0]["id"] != body["items"][0]["id"]
        assert after["next_cursor"] is None
        assert client.get("/api/v1/exhibits", params={"themes": "wrong"}).json()["items"] == []
        assert (
            client.get("/api/v1/exhibits", params={"locale": "zh-CN", "q": "测试戏剧"}).json()[
                "total"
            ]
            == 2
        )
        detail = client.get(f"/api/v1/exhibits/{exhibit.id}").json()
        assert detail["sources"][0]["passages"][0]["id"] == "test-p-a"
        assert client.get("/api/v1/exhibits/test-e-draft").status_code == 404
        assert client.get("/api/v1/sources/test-s-draft").status_code == 404
        assert client.get("/api/v1/exhibits", params={"limit": 51}).status_code == 422
        review_record(db, "source", source.id, "withdrawn", "TEST", "Test", True)
        assert client.get(f"/api/v1/exhibits/{exhibit.id}").status_code == 404
        assert client.get(f"/api/v1/sources/{source.id}").status_code == 404
        assert exhibit.id not in [e["id"] for e in client.get("/api/v1/exhibits").json()["items"]]
        app.state.engine = engine


def payload(identifier: int = 90000001) -> dict:
    return {
        "objectID": identifier,
        "title": "Synthetic bowl",
        "isPublicDomain": True,
        "primaryImage": "https://images.metmuseum.org/test.jpg",
        "country": "China",
        "city": "",
        "culture": "Chinese",
        "repository": "Metropolitan Museum",
    }


def fake_import(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, data: dict) -> None:
    monkeypatch.setattr(content, "ROOT", tmp_path)
    monkeypatch.setattr(met_import, "ROOT", tmp_path)
    monkeypatch.setattr(met_import, "CACHE", tmp_path / ".local/met")
    monkeypatch.setattr(
        met_import, "fetch_json", lambda *args: (data, json.dumps(data), datetime.now(UTC))
    )
    monkeypatch.setattr(
        met_import, "download", lambda *args: b"\xff\xd8\xffsynthetic JPEG test bytes"
    )


def test_import_idempotence_payload_hash_and_changed_rights(
    db: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = payload()
    fake_import(monkeypatch, tmp_path, data)
    first = met_import.import_object(db, data["objectID"])
    before = counts(db)
    again = met_import.import_object(db, data["objectID"])
    assert counts(db) == before and again["source_hash"] == first["source_hash"]
    source = db.get(Source, "met-source-90000001")
    assert source.raw_payload == json.dumps(data)
    assert source.raw_hash == hashlib.sha256(source.raw_payload.encode()).hexdigest()
    assert (
        db.scalar(
            select(func.count()).select_from(Media).where(Media.artifact_id == "met-90000001")
        )
        == 1
    )
    artifact = db.get(Artifact, "met-90000001")
    assert artifact.current_location == "Metropolitan Museum"
    assert artifact.origin["country"] == "China" and artifact.origin["city"] == ""
    assert artifact.status == "draft"
    for kind, identifier in [
        ("source", source.id),
        ("media", "met-image-90000001"),
        ("artifact", artifact.id),
    ]:
        approve(db, kind, identifier)
    assert artifact.id in [a.id for a in content.published_artifacts(db)]
    met_import.import_object(db, data["objectID"], True)
    assert artifact.id in [a.id for a in content.published_artifacts(db)]
    data["isPublicDomain"] = False
    met_import.import_object(db, data["objectID"], True)
    assert artifact.id not in [a.id for a in content.published_artifacts(db)]
    assert db.get(Media, "met-image-90000001").rights_status == "blocked"


def test_corrupt_image_removed_and_repaired(
    db: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    data = payload()
    fake_import(monkeypatch, tmp_path, data)
    met_import.import_object(db, data["objectID"])
    media = db.get(Media, "met-image-90000001")
    assert content.verified_media_bytes(media)
    (tmp_path / media.storage_key).write_bytes(b"corrupted")
    assert not content.verified_media_bytes(media)
    met_import.import_object(db, data["objectID"])
    assert content.verified_media_bytes(media)
    media.storage_key = "../../outside.jpg"
    assert not content.verified_media_bytes(media)


@pytest.mark.parametrize(
    "change",
    [{"isPublicDomain": False}, {"rightsAndReproduction": "Restricted"}, {"primaryImage": ""}],
)
def test_non_public_domain_and_missing_images_never_eligible(
    db: Session, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, change: dict
) -> None:
    data = payload()
    data.update(change)
    fake_import(monkeypatch, tmp_path, data)
    outcome = met_import.import_object(db, data["objectID"])
    assert not outcome["image_downloaded"]
    assert "met-90000001" not in [a.id for a in content.published_artifacts(db)]


def test_denied_upstream_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    class Denied:
        calls = 0

        def open(self, *args, **kwargs):
            self.calls += 1
            raise HTTPError("https://images.metmuseum.org/test.jpg", 403, "Denied", {}, None)

    opener = Denied()
    monkeypatch.setattr(met_import, "build_opener", lambda *args: opener)
    with pytest.raises(met_import.ImportFailure, match="no retry"):
        met_import.download("https://images.metmuseum.org/test.jpg")
    assert opener.calls == 1
    for url in [
        "http://images.metmuseum.org/a",
        "https://evil.example/a",
        "https://user@images.metmuseum.org/a",
    ]:
        with pytest.raises(met_import.ImportFailure, match="Untrusted"):
            met_import.checked_url(url)


def test_paginated_search_bounds_and_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(met_import.ImportFailure):
        met_import.search("China", 0, 51)
    urls = []

    def fetch(url, refresh):
        urls.append(url)
        return {"total": 2, "objectIDs": [1, 2]}, "{}", datetime.now(UTC)

    monkeypatch.setattr(met_import, "fetch_json", fetch)
    assert met_import.search("China", 10, 2) == [1, 2]
    assert "/v1.1/search?" in urls[0] and "offset=10" in urls[0] and "limit=2" in urls[0]
    with pytest.raises(met_import.ImportFailure, match="schema"):
        met_import.search("China", 0, 1)
