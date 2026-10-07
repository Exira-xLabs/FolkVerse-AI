"""Reviewed-current BM25 + BGE dense retrieval with deterministic rank fusion."""

import asyncio
import time
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from folkverse.content import published_exhibits
from folkverse.guide_embeddings import (
    MODEL_VERSION,
    EmbeddingUnavailable,
    Encoder,
    cached_index,
    checked_vectors,
)
from folkverse.guide_harness import EvidenceSnapshot, SqlEvidenceRepository, Topic, evidence_version
from folkverse.guide_retrieval import (
    EvidenceBundle,
    EvidencePassage,
    Locale,
    eligible_evidence,
    lexical_rank,
    select_bundle,
)
from folkverse.liaoning_publication import published_unit_evidence, published_unit_topics

HYBRID_VERSION = "bm25-bge-dense-rrf60-v1"


async def hybrid_retrieve(
    corpus: list[EvidencePassage],
    question: str,
    locale: Locale,
    exhibit_id: str | None,
    *,
    enabled: bool,
    index_path: Path,
    encoder: Encoder,
    timeout: float = 15,
    minimum_cosine: float = 0.3,
    limit: int = 5,
) -> EvidenceBundle:
    if locale not in {"en", "zh-CN"} or not 1 <= len(question.strip()) <= 2000:
        raise ValueError("Invalid retrieval question or locale")
    if not 1 <= limit <= 8 or not 0 <= minimum_cosine <= 1:
        raise ValueError("Invalid retrieval bounds")
    candidates = [
        p
        for p in corpus
        if p.language == locale and (exhibit_id is None or exhibit_id in p.exhibit_ids)
    ]
    lexical = lexical_rank(question, candidates)
    baseline = select_bundle(corpus, locale, lexical, limit)
    if not enabled:
        return baseline
    try:
        index = await asyncio.to_thread(cached_index, index_path)
    except FileNotFoundError:
        return baseline.model_copy(update={"embedding_status": "index_missing"})
    except (OSError, ValueError, ValidationError):
        return baseline.model_copy(update={"embedding_status": "index_invalid"})
    if not index.matches(corpus):
        return baseline.model_copy(update={"embedding_status": "index_stale"})
    if not candidates:
        return baseline.model_copy(
            update={
                "embedding_status": "ready",
                "embedding_model_version": MODEL_VERSION,
                "embedding_encoder_version": index.encoder_version,
            }
        )
    try:
        output = await encoder.encode([question], timeout)
        checked_vectors(output.vectors, 1)
    except EmbeddingUnavailable as exc:
        return baseline.model_copy(update={"embedding_status": exc.status})
    except ValueError:
        return baseline.model_copy(update={"embedding_status": "model_unavailable"})
    if output.encoder_version != index.encoder_version:
        return baseline.model_copy(update={"embedding_status": "encoder_changed"})
    query = output.vectors[0]
    vectors = {row.passage_id: row.vector for row in index.rows}
    dense = [
        (sum(a * b for a, b in zip(query, vectors[p.passage_id], strict=True)), p)
        for p in candidates
    ]
    dense = [(score, p) for score, p in dense if score >= minimum_cosine]
    dense.sort(key=lambda pair: (-pair[0], pair[1].passage_id))
    # Reciprocal rank fusion prevents unrelated raw BM25/cosine scales from being compared.
    scores: dict[str, float] = {}
    by_id = {p.passage_id: p for p in candidates}
    for ranking in (lexical[:50], dense[:50]):
        for rank, (_, passage) in enumerate(ranking, 1):
            scores[passage.passage_id] = scores.get(passage.passage_id, 0) + 1 / (60 + rank)
    fused = sorted(
        [(score, by_id[pid]) for pid, score in scores.items()],
        key=lambda pair: (-pair[0], pair[1].passage_id),
    )
    return select_bundle(corpus, locale, fused, limit).model_copy(
        update={
            "mode": "hybrid",
            "retrieval_version": HYBRID_VERSION,
            "embedding_status": "ready",
            "embedding_model_version": MODEL_VERSION,
            "embedding_encoder_version": index.encoder_version,
            "query_embedding_ms": output.elapsed_ms,
        }
    )


class HybridEvidenceRepository(SqlEvidenceRepository):
    def __init__(
        self,
        engine: Engine,
        encoder: Encoder,
        index_path: Path,
        enabled: bool,
        timeout: float,
        minimum_cosine: float,
    ) -> None:
        super().__init__(engine)
        self.encoder, self.index_path, self.enabled = encoder, index_path, enabled
        self.timeout, self.minimum_cosine = timeout, minimum_cosine

    def current_snapshot(self, locale: Locale) -> tuple[list[EvidencePassage], list[Topic]]:
        with Session(self.engine) as db:
            corpus = eligible_evidence(db)
            topics = [
                Topic(exhibit_id=e.id, title=e.title[locale])
                for e in published_exhibits(db)
                if locale in e.title
            ]
            unit_evidence = published_unit_evidence()
            corpus.extend(unit_evidence)
            topics.extend(
                Topic(exhibit_id=identifier, title=names[locale])
                for identifier, names in published_unit_topics().items()
                if locale in names
            )
            return corpus, topics

    def current_versions(self, passage_ids: list[str]) -> dict[str, str]:
        result = super().current_versions(passage_ids)
        result.update(
            {
                p.passage_id: evidence_version(p)
                for p in published_unit_evidence()
                if p.passage_id in passage_ids
            }
        )
        return result

    def current(self, bundle: EvidenceBundle) -> bool:
        sql = bundle.model_copy(
            update={
                "passages": [p for p in bundle.passages if p.evidence_origin == "reviewed_corpus"]
            }
        )
        current_units = {p.passage_id: p for p in published_unit_evidence()}
        return super().current(sql) and all(
            current_units.get(p.passage_id) == p
            for p in bundle.passages
            if p.evidence_origin == "reviewed_unit"
        )

    async def load_async(
        self, question: str, locale: Locale, exhibit_id: str | None
    ) -> EvidenceSnapshot:
        started = time.perf_counter()
        corpus, topics = await asyncio.to_thread(self.current_snapshot, locale)
        database_ms = (time.perf_counter() - started) * 1000
        ranked = time.perf_counter()
        bundle = await hybrid_retrieve(
            corpus,
            question,
            locale,
            exhibit_id,
            enabled=self.enabled,
            index_path=self.index_path,
            encoder=self.encoder,
            timeout=self.timeout,
            minimum_cosine=self.minimum_cosine,
        )
        bundle.database_ms = database_ms
        bundle.ranking_ms = (time.perf_counter() - ranked) * 1000
        return EvidenceSnapshot(bundle=bundle, topics=topics)
