"""Operator-only model preparation, current-corpus batch indexing and runtime benchmark."""

import argparse
import asyncio
import importlib
import json
import platform
import statistics
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import DateTime, create_engine
from sqlalchemy.engine import Dialect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from folkverse.config import Settings
from folkverse.content_snapshot import restore
from folkverse.database import Base, make_engine
from folkverse.guide_embeddings import (
    MODEL_ID,
    MODEL_REVISION,
    MODEL_VERSION,
    EmbeddingUnavailable,
    LocalBGEEncoder,
    file_hash,
    make_index,
    read_index,
    write_index,
)
from folkverse.guide_hybrid import hybrid_retrieve
from folkverse.guide_retrieval import (
    EvidencePassage,
    Locale,
    corpus_version,
    eligible_evidence,
    lexical_rank,
    select_bundle,
)

MODEL_FILES = [
    "config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "sentence_bert_config.json",
    "sentencepiece.bpe.model",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "pytorch_model.bin",
    "1_Pooling/config.json",
]


class SnapshotDateTime(DateTime):
    """SQLite benchmark only: preserve export timestamps for unchanged review hashes."""

    def bind_processor(self, dialect: Dialect) -> Callable[[datetime | None], str | None]:
        return lambda value: value.isoformat() if value is not None else None

    def result_processor(
        self,
        dialect: Dialect,
        coltype: object,
    ) -> Callable[[str | None], datetime | None]:
        return lambda value: datetime.fromisoformat(value) if value is not None else None


def prepare(directory: Path) -> dict[str, Any]:
    # Downloads are explicit operator work, never part of serving a visitor request.
    hub = importlib.import_module("huggingface_hub")
    hub.snapshot_download(
        repo_id=MODEL_ID,
        revision=MODEL_REVISION,
        local_dir=str(directory),
        allow_patterns=MODEL_FILES,
        token=False,
    )
    files = {name: file_hash(directory / name) for name in MODEL_FILES}
    marker = {"model_version": MODEL_VERSION, "files": files}
    (directory / "folkverse-model.json").write_text(json.dumps(marker, indent=2) + "\n")
    return {
        "status": "prepared",
        "model_version": MODEL_VERSION,
        "bytes": sum((directory / name).stat().st_size for name in MODEL_FILES),
    }


async def build(settings: Settings) -> dict[str, Any]:
    engine = make_engine(settings)
    try:
        with Session(engine) as db:
            corpus = eligible_evidence(db)
        index = await make_index(corpus, LocalBGEEncoder(settings.embedding_model_dir))
        # Building can be slow: refuse publication if ANY eligible metadata changed meanwhile.
        with Session(engine) as db:
            if corpus_version(eligible_evidence(db)) != index.corpus_version:
                raise ValueError("Corpus changed while indexing; rebuild required")
        write_index(settings.embedding_index_path, index)
        return {
            "status": "indexed",
            "passages": len(index.rows),
            "model_version": index.model_version,
            "corpus_version": index.corpus_version,
            "encoder_version": index.encoder_version,
        }
    finally:
        engine.dispose()


async def benchmark(
    corpus: list[EvidencePassage],
    settings: Settings,
    output: Path,
    provenance: str,
    iterations: int,
) -> dict[str, Any]:
    encoder = LocalBGEEncoder(settings.embedding_model_dir)
    queries: list[tuple[Locale, str]] = [
        ("en", "Fuzhou shadow puppetry"),
        ("zh-CN", "复州皮影戏"),
        ("en", "shadow theatre regional inventory"),
        ("zh-CN", "瓦房店传统戏剧名录"),
        ("en", "Qin dynasty emperor birth date"),
        ("zh-CN", "秦始皇出生年月"),
    ]
    cases: list[dict[str, Any]] = []
    lexical_times: list[float] = []
    for locale, question in queries:
        candidates = [p for p in corpus if p.language == locale]
        baseline = None
        for _ in range(iterations):
            started = time.perf_counter()
            baseline = select_bundle(corpus, locale, lexical_rank(question, candidates), 5)
            lexical_times.append((time.perf_counter() - started) * 1000)
        assert baseline is not None
        started = time.perf_counter()
        hybrid = await hybrid_retrieve(
            corpus,
            question,
            locale,
            None,
            enabled=True,
            index_path=output,
            encoder=encoder,
            timeout=settings.embedding_query_timeout_seconds,
            minimum_cosine=settings.embedding_min_cosine,
        )
        cases.append(
            {
                "locale": locale,
                "question": question,
                "lexical_ids": [p.passage_id for p in baseline.passages],
                "hybrid_ids": [p.passage_id for p in hybrid.passages],
                "mode": hybrid.mode,
                "embedding_status": hybrid.embedding_status,
                "query_embedding_ms": hybrid.query_embedding_ms,
                "hybrid_total_ms": (time.perf_counter() - started) * 1000,
            }
        )
    return {
        "provenance": provenance,
        "corpus_version": corpus_version(corpus),
        "passages": len(corpus),
        "model_version": MODEL_VERSION,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "iterations_per_lexical_query": iterations,
        "lexical_ms_median": statistics.median(lexical_times),
        "lexical_ms_max": max(lexical_times),
        "cases": cases,
        "quality_score": None,
        "note": "Diagnostic queries, not held-out expert evaluation. "
        "Lexical timing excludes database eligibility reads. Each dense query loads a CPU worker; "
        "cold start and artifact verification are included in query_embedding_ms.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "build", "inspect", "benchmark"])
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Benchmark exported snapshot in disposable SQLite; never serve it",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--iterations", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 1000:
        parser.error("Iterations must be 1 to 1000")
    if args.manifest and args.command != "benchmark":
        parser.error("Snapshots are allowed only for labelled offline benchmarks")
    settings = Settings()
    engine = None
    try:
        if args.command == "prepare":
            result = prepare(settings.embedding_model_dir)
        elif args.command == "build":
            result = asyncio.run(build(settings))
        elif args.command == "inspect":
            index = read_index(settings.embedding_index_path)
            result = {
                "model_version": index.model_version,
                "encoder_version": index.encoder_version,
                "corpus_version": index.corpus_version,
                "passages": len(index.rows),
            }
        else:
            if args.manifest:
                engine = create_engine("sqlite://")
                # SQLite's standard adapter drops timezones, breaking real export review hashes.
                # Keep every hash/publication check; only adapt the isolated benchmark storage.
                engine.dialect.colspecs = {**engine.dialect.colspecs, DateTime: SnapshotDateTime}
                Base.metadata.create_all(engine)
                with Session(engine) as db:
                    restore(db, args.manifest)
                    db.commit()
                    corpus = eligible_evidence(db)
                provenance = "offline_export_not_live_database"
            else:
                engine = make_engine(settings)
                with Session(engine) as db:
                    corpus = eligible_evidence(db)
                provenance = "current_database"
            # Snapshot indexes are temporary and never written to the configured runtime path.
            import tempfile

            with tempfile.TemporaryDirectory(prefix="folkverse-benchmark-") as folder:
                index_path = Path(folder) / "index.json"
                build_started = time.perf_counter()
                build_status = "ready"
                try:
                    index = asyncio.run(
                        make_index(
                            corpus, LocalBGEEncoder(settings.embedding_model_dir), timeout=120
                        )
                    )
                    write_index(index_path, index)
                except EmbeddingUnavailable as exc:
                    build_status = exc.status
                build_ms = (time.perf_counter() - build_started) * 1000
                report = asyncio.run(
                    benchmark(corpus, settings, index_path, provenance, args.iterations)
                )
                report["index_build_status"] = build_status
                report["index_build_ms"] = build_ms
                # Do not present the absent index reason as a successful model benchmark.
                if build_status != "ready":
                    report["dense_runtime_verified"] = False
                else:
                    report["dense_runtime_verified"] = all(
                        case["mode"] == "hybrid" for case in report["cases"]
                    )
                result = report
            if args.output:
                if args.output.resolve() == settings.embedding_index_path.resolve():
                    raise ValueError("Benchmark output must not replace the runtime index")
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except SQLAlchemyError:
        parser.exit(1, "Current museum database unavailable; no production index was written.\n")
    except (EmbeddingUnavailable, ImportError, OSError, ValueError):
        parser.exit(1, "Model/index unavailable or invalid; no successful build is claimed.\n")
    except Exception:
        parser.exit(
            1, "Model preparation failed; check official model connectivity and dependencies.\n"
        )
    finally:
        if engine:
            engine.dispose()


if __name__ == "__main__":
    main()
