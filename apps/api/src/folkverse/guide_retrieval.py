"""Uncached, reviewed-only lexical baseline. Retrieval is not claim validation."""

import hashlib
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from folkverse.content import fingerprint, passage_eligible, published_exhibits
from folkverse.content_models import Claim, ClaimEvidence, ExhibitRegion, Passage, Review, Source

Locale = Literal["en", "zh-CN"]
RETRIEVAL_VERSION = "lexical-bm25-cjk-v2"
MAX_BUNDLE_CHARACTERS = 12000


class EvidencePassage(BaseModel):
    passage_id: str
    source_id: str
    text: str
    language: Locale
    locator: str
    rights_basis: str
    institution: str
    source_title: str
    canonical_url: str
    fetched_at: datetime
    reviewed_at: datetime | None
    reviewer: str
    review_id: str
    content_hash: str
    exhibit_ids: list[str]
    region_ids: list[str]
    evidence_origin: Literal[
        "reviewed_corpus", "reviewed_unit", "official_lookup", "diagnostic_candidate"
    ] = "reviewed_corpus"
    classification: Literal[
        "source_statement", "history", "interpretation", "folklore", "creative_adaptation"
    ] = "source_statement"
    statement_variants: list[str] = Field(default_factory=list)
    required_support_ids: list[str] = Field(default_factory=list)


class EvidenceBundle(BaseModel):
    mode: Literal["lexical_only", "hybrid"] = "lexical_only"
    retrieval_version: str = RETRIEVAL_VERSION
    corpus_version: str
    locale: Locale
    passages: list[EvidencePassage]
    # A match only means evidence was found; an answer still needs support validation.
    status: Literal["evidence_found", "no_matching_evidence"]
    embedding_status: Literal[
        "disabled",
        "ready",
        "model_unavailable",
        "index_missing",
        "index_stale",
        "index_invalid",
        "model_timeout",
        "model_busy",
        "encoder_changed",
    ] = "disabled"
    embedding_model_version: str | None = None
    embedding_encoder_version: str | None = None
    query_embedding_ms: float | None = None
    database_ms: float | None = None
    ranking_ms: float | None = None


class CoverageIndex(BaseModel):
    corpus_version: str
    passage_counts: dict[str, int]
    source_ids: list[str]
    exhibit_ids: list[str]
    region_ids: list[str]
    # No structured reviewed period/person/object assertions exist yet.
    periods: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    objects: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(
        default_factory=lambda: [
            "Period, dynasty, person and object coverage is not indexed.",
            "A lexical match does not establish support for a question or historical claim.",
            "No reviewed translations; dense retrieval needs a current offline index.",
        ]
    )


def tokenize(text: str) -> list[str]:
    """Latin words and overlapping CJK bigrams, without a downloaded segmenter."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    tokens = re.findall(r"[a-z0-9]+", normalized)
    for run in re.findall(r"[\u3400-\u9fff]+", normalized):
        tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
        if len(run) == 1:
            tokens.append(run)
    return tokens


def eligible_evidence(db: Session) -> list[EvidencePassage]:
    """Reuse hash-bound publication gates; expose only published claim evidence."""
    db.flush()
    db.expire_all()  # Discard stale ORM copies after external editorial changes.
    associations: dict[str, set[str]] = {}
    regions: dict[str, list[str]] = {}
    for exhibit in published_exhibits(db):
        regions[exhibit.id] = sorted(
            db.scalars(
                select(ExhibitRegion.region_id).where(ExhibitRegion.exhibit_id == exhibit.id)
            )
        )
        for pid in db.scalars(
            select(ClaimEvidence.passage_id).join(Claim).where(Claim.exhibit_id == exhibit.id)
        ):
            associations.setdefault(pid, set()).add(exhibit.id)
    result = []
    for pid, exhibits in sorted(associations.items()):
        passage = db.get(Passage, pid)
        if not passage or passage.language not in {"en", "zh-CN"}:
            continue
        if not passage_eligible(db, passage):
            continue
        source = db.get(Source, passage.source_id)
        review = db.get(Review, passage.review_id)
        assert source is not None and review is not None
        result.append(
            EvidencePassage(
                passage_id=pid,
                source_id=source.id,
                text=passage.text,
                language=passage.language,
                locator=passage.locator,
                rights_basis=passage.rights_basis,
                institution=source.institution,
                source_title=source.title,
                canonical_url=source.canonical_url,
                fetched_at=source.fetched_at,
                reviewed_at=review.reviewed_at,
                review_id=review.id,
                reviewer=review.reviewer,
                content_hash=fingerprint(db, passage),
                exhibit_ids=sorted(exhibits),
                region_ids=sorted({r for eid in exhibits for r in regions[eid]}),
            )
        )
    return result


def corpus_version(passages: list[EvidencePassage]) -> str:
    payload = [p.model_dump(mode="json") for p in sorted(passages, key=lambda p: p.passage_id)]
    return (
        "corpus_"
        + hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
    )


def coverage_index(db: Session) -> CoverageIndex:
    passages = eligible_evidence(db)
    return CoverageIndex(
        corpus_version=corpus_version(passages),
        passage_counts={
            locale: sum(p.language == locale for p in passages) for locale in ("en", "zh-CN")
        },
        source_ids=sorted({p.source_id for p in passages}),
        exhibit_ids=sorted({eid for p in passages for eid in p.exhibit_ids}),
        region_ids=sorted({rid for p in passages for rid in p.region_ids}),
    )


def retrieve(
    db: Session, question: str, locale: Locale, exhibit_id: str | None = None, limit: int = 5
) -> EvidenceBundle:
    if locale not in {"en", "zh-CN"} or not 1 <= len(question.strip()) <= 2000:
        raise ValueError("Expected a nonempty question up to 2000 characters and supported locale")
    if not 1 <= limit <= 8:
        raise ValueError("Evidence limit must be between 1 and 8")
    corpus = eligible_evidence(db)
    candidates = [
        p
        for p in corpus
        if p.language == locale and (exhibit_id is None or exhibit_id in p.exhibit_ids)
    ]
    ranked = lexical_rank(question, candidates)
    return select_bundle(corpus, locale, ranked, limit)


def lexical_rank(
    question: str,
    candidates: list[EvidencePassage],
) -> list[tuple[float, EvidencePassage]]:
    clean_question = re.sub(
        r"介绍一下|解释一下|请问|是什么|告诉我|用简单的话|详细介绍", "", question
    )
    stop = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "of",
        "and",
        "or",
        "to",
        "in",
        "for",
        "what",
        "which",
        "how",
        "does",
        "do",
        "can",
        "you",
        "me",
        "please",
        "tell",
        "about",
        "explain",
        "it",
        "this",
        "that",
        "i",
        "my",
        "we",
        "with",
    }
    query = set(tokenize(clean_question)) - stop
    documents = [Counter(tokenize(p.text)) for p in candidates]
    average = sum(sum(d.values()) for d in documents) / max(1, len(documents))
    frequencies = Counter(term for d in documents for term in query & d.keys())
    ranked: list[tuple[float, EvidencePassage]] = []
    for passage, document in zip(candidates, documents, strict=True):
        score = 0.0
        for term in query & document.keys():
            frequency = frequencies[term]
            inverse = math.log(1 + (len(documents) - frequency + 0.5) / (frequency + 0.5))
            tf = document[term]
            score += (
                inverse
                * tf
                * 2.2
                / (tf + 1.2 * (0.25 + 0.75 * sum(document.values()) / max(1, average)))
            )
        if score > 0:
            ranked.append((score, passage))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].passage_id))
    return ranked


def select_bundle(
    corpus: list[EvidencePassage],
    locale: Locale,
    ranked: list[tuple[float, EvidencePassage]],
    limit: int,
) -> EvidenceBundle:
    selected: list[EvidencePassage] = []
    characters = 0
    for _, passage in ranked:
        if len(selected) == limit:
            break
        if characters + len(passage.text) > MAX_BUNDLE_CHARACTERS:
            continue  # Never truncate a passage and silently change its evidence.
        selected.append(passage)
        characters += len(passage.text)
    return EvidenceBundle(
        corpus_version=corpus_version(corpus),
        locale=locale,
        passages=selected,
        status="evidence_found" if selected else "no_matching_evidence",
    )


def bundle_is_current(db: Session, bundle: EvidenceBundle) -> bool:
    """Publication-time recheck, including source metadata and dependency changes."""
    current = {p.passage_id: p for p in eligible_evidence(db)}
    return all(current.get(p.passage_id) == p for p in bundle.passages)


def main() -> None:
    """Inspect the real configured corpus without starting a provider or chat session."""
    import argparse

    from pydantic import ValidationError
    from sqlalchemy.exc import SQLAlchemyError

    from folkverse.config import Settings
    from folkverse.database import make_engine

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", help="Retrieve evidence; omit to inspect coverage")
    parser.add_argument("--locale", choices=["en", "zh-CN"], default="en")
    parser.add_argument("--exhibit-id")
    args = parser.parse_args()
    try:
        settings = Settings()
    except ValidationError:
        parser.exit(1, "Museum configuration is invalid; check local server settings.\n")
    engine = make_engine(settings)
    try:
        with Session(engine) as db:
            result = (
                retrieve(db, args.question, args.locale, args.exhibit_id)
                if args.question is not None
                else coverage_index(db)
            )
            print(result.model_dump_json(indent=2))
    except SQLAlchemyError:
        parser.exit(1, "Museum database unavailable; no evidence or coverage was returned.\n")
    except ValueError:
        parser.exit(1, "Question must contain 1 to 2000 non-whitespace-bounded characters.\n")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
