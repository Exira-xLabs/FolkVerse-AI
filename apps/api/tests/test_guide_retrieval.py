"""Portable retrieval safety tests; synthetic approvals are never exported."""

from collections.abc import Iterator
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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
from folkverse.database import Base
from folkverse.guide_retrieval import (
    bundle_is_current,
    coverage_index,
    retrieve,
    tokenize,
)


@pytest.fixture
def db() -> Iterator[Session]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            Region(id="region", names={"en": "Test", "zh-CN": "测试"},
                   approved_geometry_ref=None),
            Source(id="source", institution="SYNTHETIC TEST", title="Test inventory",
                   canonical_url="https://example.org/inventory", external_id="test",
                   fetched_at=datetime(2026, 10, 6), raw_hash="test", raw_payload="{}",
                   rights_basis="Synthetic test text"),
            Exhibit(id="exhibit", title={"en": "Test", "zh-CN": "测试"},
                    summary={"en": "Test", "zh-CN": "测试"}, themes=["theatre"],
                    estimated_minutes=3),
        ])
        session.flush()
        session.add_all([
            ExhibitRegion(exhibit_id="exhibit", region_id="region", geographic_role="practice"),
            Passage(id="passage-en", source_id="source", language="en",
                    text="Fuzhou shadow puppetry is listed as traditional theatre in Wafangdian.",
                    locator="Test entry", rights_basis="Synthetic test text"),
            Passage(id="passage-zh", source_id="source", language="zh-CN",
                    text="复州皮影戏列入传统戏剧，地区为瓦房店。", locator="测试条目",
                    rights_basis="Synthetic test text"),
            Claim(id="claim", exhibit_id="exhibit", text="Synthetic inventory claim"),
        ])
        session.flush()
        session.add_all([ClaimEvidence(claim_id="claim", passage_id=f"passage-{lang}")
                         for lang in ["en", "zh"]])
        session.flush()
        for kind, identifier in [("region", "region"), ("source", "source"),
                                 ("passage", "passage-en"), ("passage", "passage-zh"),
                                 ("claim", "claim"), ("exhibit", "exhibit")]:
            review_record(session, kind, identifier, "approved", "AUTOMATED TEST FIXTURE",
                          "Synthetic test, no real editorial approval", True, True)
        session.commit()
        yield session
    engine.dispose()


@pytest.mark.parametrize(("locale", "question", "pid"), [
    ("en", "Where is Fuzhou shadow puppetry listed?", "passage-en"),
    ("zh-CN", "复州皮影戏在哪个地区？", "passage-zh"),
])
def test_bilingual_evidence_and_real_source_metadata(
    db: Session, locale: str, question: str, pid: str
) -> None:
    bundle = retrieve(db, question, locale)  # type: ignore[arg-type]
    assert bundle.mode == "lexical_only"
    assert bundle.embedding_status == "disabled"
    assert [p.passage_id for p in bundle.passages] == [pid]
    assert bundle.passages[0].source_id == "source"
    assert bundle.passages[0].canonical_url == "https://example.org/inventory"
    assert bundle_is_current(db, bundle)


@pytest.mark.parametrize(("locale", "question"), [
    ("en", "Qin dynasty emperor chronology"), ("zh-CN", "秦始皇出生年月"),
])
def test_absent_coverage_has_no_evidence(db: Session, locale: str, question: str) -> None:
    bundle = retrieve(db, question, locale)  # type: ignore[arg-type]
    assert bundle.status == "no_matching_evidence"
    assert not bundle.passages


@pytest.mark.parametrize(("kind", "identifier"), [
    ("source", "source"), ("passage", "passage-en"),
    ("exhibit", "exhibit"), ("claim", "claim"), ("region", "region"),
])
def test_withdrawal_invalidates_retrieval_and_existing_bundle(
    db: Session, kind: str, identifier: str
) -> None:
    bundle = retrieve(db, "shadow puppetry", "en")
    assert bundle.passages
    before = bundle.corpus_version
    review_record(db, kind, identifier, "withdrawn", "AUTOMATED TEST FIXTURE",
                  "Synthetic withdrawal", True)
    db.commit()
    assert not bundle_is_current(db, bundle)
    after = retrieve(db, "shadow puppetry", "en")
    assert not after.passages
    assert after.corpus_version != before


def test_unreviewed_edit_does_not_retain_approval(db: Session) -> None:
    bundle = retrieve(db, "shadow puppetry", "en")
    passage = db.get(Passage, "passage-en")
    assert passage is not None
    passage.text = "Invented replacement claiming imperial provenance"
    db.commit()
    assert not bundle_is_current(db, bundle)
    assert not retrieve(db, "imperial provenance", "en").passages


def test_pending_rights_removes_evidence(db: Session) -> None:
    passage = db.get(Passage, "passage-en")
    assert passage is not None
    passage.rights_status = "pending"
    db.commit()
    assert not retrieve(db, "shadow puppetry", "en").passages


def test_exhibit_context_cannot_include_hidden_or_other_exhibits(db: Session) -> None:
    assert retrieve(db, "shadow puppetry", "en", "exhibit").passages
    assert not retrieve(db, "shadow puppetry", "en", "draft-or-missing").passages


def test_coverage_is_explicit_and_does_not_infer_dynasties(db: Session) -> None:
    coverage = coverage_index(db)
    assert coverage.passage_counts == {"en": 1, "zh-CN": 1}
    assert coverage.source_ids == ["source"]
    assert coverage.exhibit_ids == ["exhibit"]
    assert coverage.region_ids == ["region"]
    assert not coverage.periods and not coverage.people and not coverage.objects
    assert coverage.gaps
    assert coverage.corpus_version == retrieve(db, "shadow", "en").corpus_version


@pytest.mark.parametrize("question", ["", "   ", "x" * 2001])
def test_question_limits(db: Session, question: str) -> None:
    with pytest.raises(ValueError):
        retrieve(db, question, "en")


def test_cjk_and_fullwidth_tokens() -> None:
    assert "皮影" in tokenize("复州皮影戏")
    assert tokenize("ＦＵＺＨＯＵ") == ["fuzhou"]


def test_draft_and_unattached_passages_are_excluded(db: Session) -> None:
    db.add(Passage(id="unattached", source_id="source", language="en",
                   text="Secret unattached dynasty chronology", locator="Test",
                   rights_basis="Synthetic test text"))
    db.flush()
    assert not retrieve(db, "dynasty chronology", "en").passages
    review_record(db, "passage", "unattached", "approved", "AUTOMATED TEST FIXTURE",
                  "Synthetic approval without exhibit association", True, True)
    db.commit()
    assert not retrieve(db, "dynasty chronology", "en").passages


def test_source_metadata_edits_invalidate_review_and_bundle(db: Session) -> None:
    bundle = retrieve(db, "shadow puppetry", "en")
    source = db.get(Source, "source")
    assert source is not None
    source.canonical_url = "https://example.org/unreviewed-replacement"
    db.commit()
    assert not bundle_is_current(db, bundle)
    assert not retrieve(db, "shadow puppetry", "en").passages


def test_oversized_passage_is_omitted_without_truncation(db: Session) -> None:
    passage = db.get(Passage, "passage-en")
    assert passage is not None
    passage.text = "shadow puppetry " * 1000
    db.flush()
    review_record(db, "passage", passage.id, "approved", "AUTOMATED TEST FIXTURE",
                  "Synthetic oversized passage", True, True)
    db.commit()
    assert coverage_index(db).passage_counts["en"] == 1
    assert not retrieve(db, "shadow puppetry", "en").passages


@pytest.mark.parametrize("limit", [0, 9])
def test_bundle_limit(db: Session, limit: int) -> None:
    with pytest.raises(ValueError):
        retrieve(db, "shadow", "en", limit=limit)


def test_external_withdrawal_refreshes_existing_orm_state(db: Session) -> None:
    bundle = retrieve(db, "shadow puppetry", "en")
    assert bundle.passages
    assert db.get(Source, "source") is not None
    with Session(db.get_bind()) as editor:
        source = editor.get(Source, "source")
        assert source is not None
        source.status = "withdrawn"
        editor.commit()
    assert not bundle_is_current(db, bundle)
    assert not retrieve(db, "shadow puppetry", "en").passages
