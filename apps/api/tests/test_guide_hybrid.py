"""Synthetic vectors/reviews verify boundaries; they do not benchmark BGE quality."""

import asyncio
import json

import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session
from test_guide_retrieval import db as db  # noqa: F401

from folkverse.content import review_record
from folkverse.content_models import Passage, Source
from folkverse.guide_embeddings import (
    DIMENSIONS,
    MODEL_VERSION,
    EmbeddingIndex,
    EmbeddingOutput,
    EmbeddingUnavailable,
    IndexRow,
    LocalBGEEncoder,
    make_index,
    read_index,
    write_index,
)
from folkverse.guide_harness import GuideHarness
from folkverse.guide_hybrid import hybrid_retrieve
from folkverse.guide_retrieval import eligible_evidence


def vector(axis=0):
    return [float(i == axis) for i in range(DIMENSIONS)]


class FakeEncoder:
    def __init__(self, version="fixture_encoder", failure=None):
        self.version, self.failure, self.calls = version, failure, 0

    async def encode(self, texts, timeout):
        self.calls += 1
        if self.failure:
            raise EmbeddingUnavailable(self.failure)
        return EmbeddingOutput(
            vectors=[vector() for _ in texts], encoder_version=self.version, elapsed_ms=1.0
        )


def indexed(db, tmp_path):
    corpus = eligible_evidence(db)
    encoder = FakeEncoder()
    index = asyncio.run(make_index(corpus, encoder))
    path = tmp_path / "index.json"
    write_index(path, index)
    encoder.calls = 0
    return corpus, encoder, index, path


def run(corpus, encoder, path, question="Synonym with no lexical overlap", locale="en", **changes):
    options = dict(enabled=True, index_path=path, encoder=encoder)
    options.update(changes)
    return asyncio.run(hybrid_retrieve(corpus, question, locale, None, **options))


@pytest.mark.parametrize("locale,identifier", [("en", "passage-en"), ("zh-CN", "passage-zh")])
def test_dense_synonym_finds_only_current_language(db, tmp_path, locale, identifier):
    corpus, encoder, index, path = indexed(db, tmp_path)
    answer = run(corpus, encoder, path, locale=locale)
    assert answer.mode == "hybrid" and answer.embedding_status == "ready"
    assert [p.passage_id for p in answer.passages] == [identifier]
    assert answer.embedding_model_version == MODEL_VERSION
    assert answer.embedding_encoder_version == index.encoder_version
    assert answer.query_embedding_ms == 1.0


def test_disabled_and_missing_index_skip_model(db, tmp_path):
    corpus, encoder, _, path = indexed(db, tmp_path)
    answer = run(corpus, encoder, path, "shadow", enabled=False)
    assert answer.mode == "lexical_only" and answer.embedding_status == "disabled"
    path.unlink()
    answer = run(corpus, encoder, path, "shadow")
    assert answer.embedding_status == "index_missing" and answer.passages
    assert encoder.calls == 0


@pytest.mark.parametrize("status", ["model_unavailable", "model_timeout", "model_busy"])
def test_model_failures_preserve_explicit_lexical_results(db, tmp_path, status):
    corpus, _, _, path = indexed(db, tmp_path)
    answer = run(corpus, FakeEncoder(failure=status), path, "shadow")
    assert answer.mode == "lexical_only" and answer.embedding_status == status
    assert [p.passage_id for p in answer.passages] == ["passage-en"]
    assert answer.embedding_model_version is None and answer.query_embedding_ms is None


@pytest.mark.parametrize(
    "kind,id",
    [
        ("source", "source"),
        ("passage", "passage-en"),
        ("claim", "claim"),
        ("exhibit", "exhibit"),
        ("region", "region"),
    ],
)
def test_withdrawal_invalidates_index_and_never_resurrects_evidence(db, tmp_path, kind, id):
    _, encoder, _, path = indexed(db, tmp_path)
    review_record(db, kind, id, "withdrawn", "AUTOMATED TEST FIXTURE", "Synthetic withdrawal", True)
    db.commit()
    current = eligible_evidence(db)
    answer = run(current, encoder, path, "shadow")
    assert answer.mode == "lexical_only" and answer.embedding_status == "index_stale"
    assert "passage-en" not in [p.passage_id for p in answer.passages]
    assert encoder.calls == 0


@pytest.mark.parametrize("change", ["text", "metadata", "review", "rights"])
def test_version_changes_invalidate_all_embeddings(db, tmp_path, change):
    _, encoder, _, path = indexed(db, tmp_path)
    if change == "metadata":
        db.get(Source, "source").title = "Changed attribution"
    elif change == "review":
        review_record(
            db,
            "passage",
            "passage-en",
            "approved",
            "NEW SYNTHETIC REVIEW",
            "Synthetic new review",
            True,
            True,
        )
    elif change == "rights":
        db.get(Passage, "passage-en").rights_status = "pending"
    else:
        db.get(Passage, "passage-en").text += " Unreviewed addition."
    db.commit()
    answer = run(eligible_evidence(db), encoder, path, "shadow")
    assert answer.embedding_status == "index_stale" and encoder.calls == 0


def test_model_and_encoder_versions_cannot_mix(db, tmp_path):
    corpus, encoder, index, path = indexed(db, tmp_path)
    write_index(path, index.model_copy(update={"model_version": "different-model"}))
    assert run(corpus, encoder, path).embedding_status == "index_stale"
    write_index(path, index)
    assert (
        run(corpus, FakeEncoder(version="changed-runtime"), path).embedding_status
        == "encoder_changed"
    )


@pytest.mark.parametrize(
    "mutation", ["nan", "zero", "dimension", "duplicate", "extra", "truncated"]
)
def test_corrupt_artifact_falls_back_without_query(db, tmp_path, mutation):
    corpus, encoder, index, path = indexed(db, tmp_path)
    data = index.model_dump()
    if mutation == "nan":
        data["rows"][0]["vector"][0] = float("nan")
    elif mutation == "zero":
        data["rows"][0]["vector"] = [0.0] * DIMENSIONS
    elif mutation == "dimension":
        data["rows"][0]["vector"] = [1.0]
    elif mutation == "duplicate":
        data["rows"].append(data["rows"][0])
    elif mutation == "extra":
        data["untrusted"] = "invented"
    path.write_text("{" if mutation == "truncated" else json.dumps(data))
    answer = run(corpus, encoder, path, "shadow")
    assert answer.mode == "lexical_only" and answer.embedding_status == "index_invalid"
    assert answer.passages and encoder.calls == 0


def test_low_dense_similarity_and_scope_do_not_force_results(db, tmp_path):
    corpus, encoder, index, path = indexed(db, tmp_path)
    index.rows[0].vector = vector(1)
    write_index(path, index)
    assert not run(corpus, encoder, path).passages
    answer = asyncio.run(
        hybrid_retrieve(
            corpus, "shadow", "en", "draft", enabled=True, index_path=path, encoder=encoder
        )
    )
    assert not answer.passages


def test_fusion_is_deterministic_and_preserves_whole_passage_bounds(db, tmp_path):
    corpus, encoder, index, path = indexed(db, tmp_path)
    second = corpus[0].model_copy(
        update={"passage_id": "a-tied", "text": "Unrelated complete fixture"}
    )
    corpus.append(second)
    index = asyncio.run(make_index(corpus, encoder))
    write_index(path, index)
    result = run(corpus, encoder, path, "shadow", limit=1)
    assert [p.passage_id for p in result.passages] == ["passage-en"]
    result = run(corpus, encoder, path)
    assert [p.passage_id for p in result.passages] == ["a-tied", "passage-en"]
    corpus[0] = corpus[0].model_copy(update={"text": "x" * 12001})
    index = index.model_copy(
        update={
            "corpus_version": __import__(
                "folkverse.guide_retrieval", fromlist=["corpus_version"]
            ).corpus_version(corpus)
        }
    )
    write_index(path, index)
    assert all(len(p.text) <= 12000 for p in run(corpus, encoder, path).passages)


def test_atomic_write_and_read_roundtrip(db, tmp_path):
    _, _, index, path = indexed(db, tmp_path)
    assert read_index(path) == index and path.stat().st_mode & 0o777 == 0o600
    assert not list(tmp_path.glob(".index-*"))
    with pytest.raises(ValidationError):
        EmbeddingIndex(
            encoder_version="fixture",
            corpus_version="fixture",
            rows=[IndexRow(passage_id="p", content_hash="h", vector=[1.0])],
        )


@pytest.mark.parametrize("timeout,cancel", [(0.01, False), (30, True)])
def test_worker_timeout_or_cancel_kills_and_reaps(monkeypatch, tmp_path, timeout, cancel):
    async def check():
        started = asyncio.Event()

        class Process:
            returncode = None
            killed = False
            reaped = False

            async def communicate(self, payload):
                assert b"private question" in payload
                started.set()
                await asyncio.sleep(100)

            def kill(self):
                self.killed = True
                self.returncode = -9

            async def wait(self):
                self.reaped = True

        process = Process()

        async def spawn(*args, **kwargs):
            assert "private question" not in str(args)
            assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
            assert "PRIVATE_API_KEY" not in kwargs["env"]
            assert "DATABASE_URL" not in kwargs["env"]
            assert "CUSTOM_PROVIDER_CREDENTIAL" not in kwargs["env"]
            return process

        monkeypatch.setenv("PRIVATE_API_KEY", "fixture_secret")
        monkeypatch.setenv("DATABASE_URL", "fixture-private-database-url")
        monkeypatch.setenv("CUSTOM_PROVIDER_CREDENTIAL", "fixture-private-credential")
        monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
        (tmp_path / "folkverse-model.json").write_text("fixture")
        encoder = LocalBGEEncoder(tmp_path)
        task = asyncio.create_task(encoder.encode(["private question"], timeout))
        await started.wait()
        with pytest.raises(EmbeddingUnavailable, match="model_busy"):
            await encoder.encode(["second question"], timeout)
        if cancel:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            with pytest.raises(EmbeddingUnavailable, match="model_timeout"):
                await task
        assert process.killed and process.reaped

    asyncio.run(check())


def test_missing_model_does_not_spawn(monkeypatch, tmp_path):
    async def spawn(*args, **kwargs):
        raise AssertionError("A missing model must not spawn or download")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    with pytest.raises(EmbeddingUnavailable, match="model_unavailable"):
        asyncio.run(LocalBGEEncoder(tmp_path).encode(["question"], 1))


def test_harness_prefers_cancellable_async_repository():
    class Repository:
        async def load_async(self, *args):
            return "fixture_snapshot"

        def load(self, *args):
            raise AssertionError("Sync embedding work would not propagate cancellation")

    harness = GuideHarness(Repository(), None, "s" * 40)
    assert asyncio.run(harness.load_snapshot("question", "en", None)) == "fixture_snapshot"


def test_failed_atomic_publication_preserves_previous_index(db, tmp_path, monkeypatch):
    _, _, index, path = indexed(db, tmp_path)
    previous = path.read_bytes()

    def fail(*args):
        raise OSError("fixture filesystem failure")

    monkeypatch.setattr("folkverse.guide_embeddings.os.replace", fail)
    with pytest.raises(OSError):
        write_index(path, index)
    assert path.read_bytes() == previous and not list(tmp_path.glob(".index-*"))


@pytest.mark.parametrize("tamper", [False, True])
def test_offline_export_benchmark_keeps_timestamp_bound_review_checks(tmp_path, tamper):
    from sqlalchemy import DateTime, create_engine

    from folkverse.config import ROOT
    from folkverse.content_snapshot import restore
    from folkverse.database import Base
    from folkverse.guide_index import SnapshotDateTime

    engine = create_engine("sqlite://")
    engine.dialect.colspecs = {**engine.dialect.colspecs, DateTime: SnapshotDateTime}
    Base.metadata.create_all(engine)
    data = json.loads((ROOT / "data/manifests/corpus.json").read_text())
    if tamper:
        next(p for p in data["passage"] if p["status"] == "approved")["text"] += " Altered."
    path = tmp_path / "export.json"
    path.write_text(json.dumps(data))
    try:
        with Session(engine) as session:
            if tamper:
                with pytest.raises(ValueError, match="hash or entity identity mismatch"):
                    restore(session, path)
            else:
                restore(session, path)
                session.commit()
                corpus = eligible_evidence(session)
                assert len(corpus) == 2
                assert {p.language for p in corpus} == {"en", "zh-CN"}
                assert all(p.fetched_at.tzinfo is not None for p in corpus)
    finally:
        engine.dispose()
