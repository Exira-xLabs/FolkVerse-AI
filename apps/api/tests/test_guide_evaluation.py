"""Independent scoring, frozen gold and actual SQL follow-up regressions."""

import asyncio
import copy
import hashlib
import hmac
import json
import time
from decimal import Decimal

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

import folkverse.guide_evaluation as evaluation
from folkverse.config import Settings
from folkverse.errors import ApiError
from folkverse.gateway_models import GatewayAttempt
from folkverse.guide_evaluation import (
    ROOT,
    EvaluationSuite,
    FixtureGateway,
    FixtureRepository,
    checked_gold,
    evaluate,
    metric,
    read_suite,
    score_case,
    snapshot_engine,
    summarize,
)
from folkverse.guide_harness import GuideAnswer, GuideHarness, GuideRequest, evidence_version
from folkverse.guide_retrieval import eligible_evidence
from folkverse.guide_review import HumanReviews, grade, template
from folkverse.provider_gateway import ProviderResult, ProviderUsage

SUITE = ROOT / "tests/evaluation/guide/v1.json"
MANIFEST = ROOT / "data/manifests/corpus.json"


@pytest.fixture(scope="module")
def run():
    return asyncio.run(evaluate(SUITE, MANIFEST, "fixture"))


@pytest.fixture
def saved_run(run, tmp_path):
    path = tmp_path / "run.json"
    path.write_text(json.dumps(run))
    return path


def test_frozen_bilingual_pairs_and_reviewed_gold():
    suite = read_suite(SUITE)
    assert len(suite.cases) >= 40
    assert {c.split for c in suite.cases} == {"development", "heldout"}
    engine = snapshot_engine(MANIFEST)
    try:
        with Session(engine) as db:
            corpus = eligible_evidence(db)
        checked_gold(suite, corpus)
        modified = suite.model_copy(deep=True)
        next(iter(modified.reviewed_claims.values())).text += " invented date 1644"
        with pytest.raises(ValueError, match="Frozen reviewed"):
            checked_gold(modified, corpus)
    finally:
        engine.dispose()


@pytest.mark.parametrize("mutation", ["split", "duplicate", "unknown_gold", "live_fault"])
def test_suite_rejects_invalid_split_gold_and_live_injections(mutation):
    data = json.loads(SUITE.read_text())
    if mutation == "split":
        data["cases"][0]["split"] = "heldout"
    elif mutation == "duplicate":
        data["cases"][1]["id"] = data["cases"][0]["id"]
    elif mutation == "unknown_gold":
        data["cases"][0]["expected_reviewed_claim_ids"] = ["invented"]
        data["cases"][0]["allowed_evidence_ids"] = ["invented"]
    else:
        next(c for c in data["cases"] if not c["live_eligible"])["live_eligible"] = True
    with pytest.raises(ValidationError):
        EvaluationSuite.model_validate(data)


@pytest.mark.parametrize("locale", ["en", "zh-CN"])
def test_sql_followup_switches_language_and_detects_previous_withdrawal(locale):
    engine = snapshot_engine(MANIFEST)
    repository = FixtureRepository(engine, "normal")
    harness = GuideHarness(repository, FixtureGateway(repository, "normal"), "test-secret-" * 4)

    async def check():
        question = (
            "Where is Fuzhou shadow puppetry listed?"
            if locale == "en"
            else "复州皮影戏在哪个地区？"
        )
        seed = await harness.answer(
            GuideRequest(question=question, locale=locale, context_consent=True), "owner"
        )
        assert seed.status == "answered" and seed.context_token
        versions = repository.current_versions(seed.evidence_ids)
        assert versions == {p.passage_id: evidence_version(p) for p in seed.sources}
        other = "zh-CN" if locale == "en" else "en"
        followup = GuideRequest(
            question="Simplify that." if other == "en" else "说简单一点。",
            locale=other,
            context_consent=True,
            context_token=seed.context_token,
        )
        result = await harness.answer(followup, "owner")
        assert result.status == "answered" and result.locale == other
        assert result.sources and all(p.language == other for p in result.sources)
        repository.withdraw()
        assert repository.current_versions(seed.evidence_ids) == {}
        revoked = await harness.answer(followup, "owner")
        assert revoked.status != "answered"
        assert not revoked.claims and not revoked.sources

    try:
        asyncio.run(check())
    finally:
        engine.dispose()


def test_empty_metrics_and_abstentions_get_no_support_credit(run):
    assert metric([], "test")["rate"] is None
    abstained = [case for case in run["cases"] if case["actual_status"] == "insufficient"]
    scores = summarize(abstained)["dimensions"]
    assert scores["claim_support"]["denominator"] == 0
    assert scores["citation_validity"]["denominator"] == 0
    assert scores["historical_correctness"]["numerator"] is None


def test_fixture_reports_no_real_usage_and_no_automatic_expertise(run):
    assert run["usage"]["real_provider_requests"] == 0
    assert run["usage"]["actual_tokens"] is None
    assert run["usage"]["actual_cost_usd"] is None
    assert run["expert_quality_verified"] is False
    assert all("context_token" not in (c["answer"] or {}) for c in run["cases"])
    assert len(run["overall"]["dimensions"]) == 7


@pytest.mark.parametrize("mutation", ["display", "citation", "claim", "reference"])
def test_scorer_independently_rejects_unsupported_publication(run, mutation):
    row = next(c for c in run["cases"] if c["actual_status"] == "answered")
    case = next(c for c in read_suite(SUITE).cases if c.id == row["id"])
    answer = GuideAnswer.model_validate(row["answer"])
    engine = snapshot_engine(MANIFEST)
    try:
        with Session(engine) as db:
            corpus = {p.passage_id: p for p in eligible_evidence(db)}
        if mutation == "display":
            answer.answer_text += "\nThis tradition originated in 1644."
        elif mutation == "citation":
            answer.evidence_ids.append("invented-source")
        elif mutation == "claim":
            answer.claims[0].text += " Invented chronology."
        else:
            answer.answer_claim_ids.append(answer.answer_claim_ids[0])
        scores = score_case(case, answer, None, corpus, None)
        assert scores["scenario_outcome"] is False
        assert scores["claim_support"] is False or scores["citation_validity"] is False
    finally:
        engine.dispose()


def test_human_worksheet_stays_pending_and_is_bound_to_run(saved_run, tmp_path):
    reviews = template(saved_run)
    assert reviews.ratings and all(r.passed is None for r in reviews.ratings)
    path = tmp_path / "reviews.json"
    path.write_text(reviews.model_dump_json())
    result = grade(saved_run, path)
    assert result["expert_quality_verified"] is False
    assert all(s["denominator"] == 0 for s in result["human_dimensions"].values())
    saved_run.write_text(saved_run.read_text() + "\n")
    with pytest.raises(ValueError, match="different run"):
        grade(saved_run, path)


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "unknown", "unattributed"])
def test_human_grading_rejects_invalid_reviews(saved_run, tmp_path, mutation):
    data = template(saved_run).model_dump(mode="json")
    if mutation == "duplicate":
        data["ratings"].append(copy.deepcopy(data["ratings"][0]))
    elif mutation == "missing":
        data["ratings"].pop()
    elif mutation == "unknown":
        data["ratings"][0]["unit_id"] = "invented"
    else:
        data["ratings"][0]["passed"] = True
    path = tmp_path / "reviews.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        grade(saved_run, path)


def test_partial_human_grading_counts_only_attributed_judgments(saved_run, tmp_path):
    data = template(saved_run).model_dump(mode="json")
    data["ratings"][0].update(
        passed=False,
        reviewer="Synthetic unit-test reviewer",
        reviewed_at="2026-10-06T00:00:00+00:00",
        rationale="Synthetic failing judgment for testing only",
        basis="Unit-test fixture, not an actual historical assessment",
        attest_human_review=True,
    )
    HumanReviews.model_validate(data)
    path = tmp_path / "reviews.json"
    path.write_text(json.dumps(data))
    result = grade(saved_run, path)
    scores = result["human_dimensions"]["historical_correctness"]
    assert scores["numerator"] == 0 and scores["denominator"] == 1
    assert scores["pending"] > 0 and result["expert_quality_verified"] is False


def test_frozen_manifest_cannot_be_silently_rebound(tmp_path):
    changed = tmp_path / "manifest.json"
    changed.write_bytes(MANIFEST.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Frozen manifest changed"):
        asyncio.run(evaluate(SUITE, changed, "fixture"))


def test_live_preflight_does_not_activate_billing_or_open_database(monkeypatch):
    settings = Settings(app_mode="demo", daily_ai_budget_usd=Decimal("0"))
    monkeypatch.setattr(evaluation, "Settings", lambda: settings)

    class ClosedEngine:
        disposed = False

        def dispose(self):
            self.disposed = True

        def connect(self):
            raise AssertionError("Disabled live evaluation must not access the database")

    engine = ClosedEngine()
    monkeypatch.setattr(evaluation, "make_engine", lambda _: engine)
    with pytest.raises(ApiError):
        asyncio.run(evaluate(SUITE, MANIFEST, "live"))
    assert engine.disposed
    assert settings.app_mode == "demo" and settings.daily_ai_budget_usd == 0


def test_usage_counts_only_this_run_and_preserves_unknown_tokens():
    engine = snapshot_engine(MANIFEST)
    settings = Settings()

    class LedgerFixture:
        calls = 0

        async def complete(self, messages, actor_id):
            self.calls += 1
            actor_hash = hmac.new(
                settings.session_secret.get_secret_value().encode(),
                actor_id.encode(),
                hashlib.sha256,
            ).hexdigest()
            with Session(engine) as db:
                db.add(
                    GatewayAttempt(
                        id=f"test-attempt-{self.calls}",
                        day="2026-10-06",
                        actor_hash=actor_hash,
                        started_at=time.time(),
                        lease_until=time.time(),
                        model="test-fixture",
                        status="completed",
                        charged_nano_usd=100,
                        prompt_tokens=3 if self.calls == 1 else None,
                        completion_tokens=2 if self.calls == 1 else None,
                    )
                )
                db.commit()
            return ProviderResult(
                payload={},
                model="test-fixture",
                attempt_id=f"test-attempt-{self.calls}",
                latency_ms=1,
                usage=ProviderUsage(prompt_tokens=3, completion_tokens=2, total_tokens=5),
            )

    gateway = LedgerFixture()
    meter = evaluation.MeteredEvaluationGateway(gateway, engine, settings)
    try:
        asyncio.run(gateway.complete([], "unrelated-operator"))
        asyncio.run(meter.complete([], "evaluation-operator"))
        usage = meter.usage()
        assert usage["real_provider_requests"] == 1
        assert usage["unknown_usage_attempts"] == 1 and usage["actual_tokens"] is None
        assert usage["budget_charge_nano_usd"] == 100
        assert usage["actual_cost_usd"] is None
        assert [a["id"] for a in usage["attempts"]] == ["test-attempt-2"]
    finally:
        engine.dispose()
