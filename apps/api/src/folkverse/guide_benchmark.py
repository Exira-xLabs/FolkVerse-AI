"""Reproducible retrieval diagnostics; candidate evaluation never publishes or approves data."""

import argparse
import asyncio
import json
import math
import platform
import statistics
import tempfile
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from folkverse.config import ROOT, Settings
from folkverse.database import make_engine
from folkverse.guide_embeddings import (
    LocalBGEEncoder,
    PersistentBGEEncoder,
    make_index,
    write_index,
)
from folkverse.guide_hybrid import hybrid_retrieve
from folkverse.guide_retrieval import (
    EvidencePassage,
    Locale,
    eligible_evidence,
    lexical_rank,
    tokenize,
)
from folkverse.liaoning_inventory import collections, digest


def legacy_rank(
    question: str, candidates: list[EvidencePassage]
) -> list[tuple[float, EvidencePassage]]:
    query = set(tokenize(question))
    documents = [Counter(tokenize(p.text)) for p in candidates]
    average = sum(sum(d.values()) for d in documents) / max(1, len(documents))
    ranked = []
    for passage, document in zip(candidates, documents, strict=True):
        score = 0.0
        for term in query & document.keys():
            frequency = sum(term in d for d in documents)
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
    return sorted(ranked, key=lambda pair: (-pair[0], pair[1].passage_id))


def candidates(folder: Path) -> list[EvidencePassage]:
    material = json.loads((folder / "launch-material.json").read_text())["materials"]
    captured = {c["source"]["id"]: c for c in collections(folder)}
    result = []
    for row in material:
        capture = captured[row["source_id"]]
        for locale in ("en", "zh-CN"):
            language: Locale = locale
            text = row["context"][locale] + " " + row["example"][locale]
            result.append(
                EvidencePassage(
                    passage_id=row["source_id"] + "-" + locale,
                    source_id=row["source_id"],
                    text=text,
                    language=language,
                    locator="launch-material:context+example",
                    rights_basis="UNAPPROVED DIAGNOSTIC CANDIDATE; NEVER SERVE",
                    institution=capture["source"]["institution"],
                    source_title=row["title"],
                    canonical_url=capture["source"]["url"],
                    fetched_at=datetime.fromisoformat(capture["fetched_at"]),
                    reviewed_at=None,
                    reviewer="",
                    review_id="unapproved_diagnostic",
                    content_hash=digest([capture["raw_sha256"], text]),
                    exhibit_ids=[],
                    region_ids=[row["city_id"]],
                    evidence_origin="diagnostic_candidate",
                )
            )
    return result


def percentiles(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "sample_size": len(values),
        "p50_ms": statistics.median(ordered),
        "p95_ms": ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)],
        "max_ms": max(ordered),
    }


def metrics(rows: list[dict[str, Any]], method: str) -> dict[str, Any]:
    positive = [r for r in rows if r["expected_source_id"] is not None]
    negative = [r for r in rows if r["expected_source_id"] is None]
    hits = sum(r["expected_source_id"] in r[method] for r in positive)
    reciprocal = sum(
        1 / (r[method].index(r["expected_source_id"]) + 1)
        if r["expected_source_id"] in r[method]
        else 0
        for r in positive
    )
    return {
        "recall_at_3_numerator": hits,
        "recall_at_3_denominator": len(positive),
        "recall_at_3": hits / max(1, len(positive)),
        "mrr_at_3": reciprocal / max(1, len(positive)),
        "negative_return_rate_numerator": sum(bool(r[method]) for r in negative),
        "negative_return_rate_denominator": len(negative),
    }


async def run(settings: Settings, folder: Path, output: Path) -> dict[str, Any]:
    corpus = candidates(folder)
    data = json.loads((folder / "retrieval-diagnostics.json").read_text())
    encoder = PersistentBGEEncoder(settings.embedding_model_dir)
    before = LocalBGEEncoder(settings.embedding_model_dir)
    started = time.perf_counter()
    baseline = await before.encode([data["cases"][0]["question"]], 60)
    cold_baseline_wall = (time.perf_counter() - started) * 1000
    rows = []
    warm_times = []
    cache_times = []
    try:
        with tempfile.TemporaryDirectory(prefix="folkverse-candidate-diagnostics-") as temporary:
            index_path = Path(temporary) / "index.json"
            index_started = time.perf_counter()
            index = await make_index(corpus, encoder, 120)
            index_ms = (time.perf_counter() - index_started) * 1000
            write_index(index_path, index)
            for case in data["cases"]:
                question = case["question"]
                locale = case["locale"]
                documents = [p for p in corpus if p.language == locale]
                old_started = time.perf_counter()
                old = legacy_rank(question, documents)
                old_ms = (time.perf_counter() - old_started) * 1000
                lexical_started = time.perf_counter()
                lexical = lexical_rank(question, documents)
                lexical_ms = (time.perf_counter() - lexical_started) * 1000
                dense_started = time.perf_counter()
                retrieval_result = await hybrid_retrieve(
                    corpus,
                    question,
                    locale,
                    None,
                    enabled=True,
                    index_path=index_path,
                    encoder=encoder,
                    timeout=5,
                    limit=3,
                )
                dense_ms = (time.perf_counter() - dense_started) * 1000
                warm_times.append(dense_ms)
                repeated_started = time.perf_counter()
                await hybrid_retrieve(
                    corpus,
                    question,
                    locale,
                    None,
                    enabled=True,
                    index_path=index_path,
                    encoder=encoder,
                    timeout=5,
                    limit=3,
                )
                cache_ms = (time.perf_counter() - repeated_started) * 1000
                cache_times.append(cache_ms)
                rows.append(
                    case
                    | {
                        "old_lexical": [p.source_id for _, p in old[:3]],
                        "lexical": [p.source_id for _, p in lexical[:3]],
                        "hybrid": [p.source_id for p in retrieval_result.passages],
                        "old_lexical_ms": old_ms,
                        "lexical_ms": lexical_ms,
                        "hybrid_wall_ms": dense_ms,
                        "repeat_wall_ms": cache_ms,
                        "embedding_status": retrieval_result.embedding_status,
                    }
                )
            resident_kib = None
            if encoder.process:
                for line in Path(f"/proc/{encoder.process.pid}/status").read_text().splitlines():
                    if line.startswith("VmRSS:"):
                        resident_kib = int(line.split()[1])

            async def concurrent(query: str) -> str:
                try:
                    await encoder.encode([query], 5)
                    return "ready"
                except Exception as exc:
                    return getattr(exc, "status", "failed")

            concurrency = await asyncio.gather(
                concurrent("New industrial landscape query"),
                concurrent("New landscape temple query"),
            )
    finally:
        await encoder.close()
    engine = make_engine(settings)
    database = []
    try:
        for _ in range(10):
            stamp = time.perf_counter()
            with Session(engine) as db:
                current = eligible_evidence(db)
            database.append((time.perf_counter() - stamp) * 1000)
    finally:
        engine.dispose()
    result = {
        "version": "retrieval-diagnostics-v1",
        "measured_at": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": platform.platform(),
            "cpu_model": next(
                (
                    line.split(":", 1)[1].strip()
                    for line in Path("/proc/cpuinfo").read_text().splitlines()
                    if line.startswith("model name")
                ),
                "unknown",
            ),
            "threads": 2,
            "encoder_version": index.encoder_version,
            "model_version": index.model_version,
        },
        "corpus": {
            "diagnostic_candidate_passages": len(corpus),
            "cities": len({r for p in corpus for r in p.region_ids}),
            "actually_eligible_database_passages": len(current),
            "expert_reviewed_expanded_sample": False,
            "candidate_index_used_by_runtime": False,
        },
        "sample": {
            "queries": len(rows),
            "corpus_fingerprint": digest([p.model_dump(mode="json") for p in corpus]),
            "query_fingerprint": digest(data),
        },
        "timing": {
            "oneshot_cold_wall_ms": cold_baseline_wall,
            "oneshot_embedding_ms": baseline.elapsed_ms,
            "persistent_startup_and_84_passage_index_ms": index_ms,
            "warm_distinct_queries": percentiles(warm_times),
            "repeat_queries": percentiles(cache_times),
            "database_eligibility_reads": percentiles(database),
            "old_lexical": percentiles([r["old_lexical_ms"] for r in rows]),
            "lexical": percentiles([r["lexical_ms"] for r in rows]),
        },
        "worker": {
            "resident_kib": resident_kib,
            "concurrency_two_outcomes": concurrency,
            "queue_capacity": 0,
            "max_lifetime_seconds": 1800,
            "max_worker_requests": 256,
            "query_cache_entries": 128,
            "shutdown_reaped": encoder.process is None,
        },
        "scores": {
            split: {
                method: metrics([r for r in rows if r["split"] == split], method)
                for method in ["old_lexical", "lexical", "hybrid"]
            }
            for split in ["development", "reserved_diagnostic"]
        },
        "cases": rows,
        "historical_correctness_score": None,
        "expert_quality_score": None,
        "limits": (
            "Source-derived candidate expectations, not human-reviewed gold or "
            "province-wide release evidence. Dense matches do not establish claim support. "
            "Full request latency is measured separately with the real provider; "
            "cold model startup is excluded from warm queries but reported explicitly."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "report/evidence/phase03-hybrid-part05/retrieval.json"
    )
    args = parser.parse_args()
    report = asyncio.run(run(Settings(), ROOT / "data/liaoning", args.output))
    print(json.dumps({k: report[k] for k in ["corpus", "timing", "worker", "scores"]}, indent=2))


if __name__ == "__main__":
    main()
