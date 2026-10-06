"""Pinned offline BGE-M3 artifacts and cancellable, network-free CPU query workers."""

import asyncio
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from folkverse.guide_retrieval import EvidencePassage, corpus_version

MODEL_ID = "BAAI/bge-m3"
MODEL_REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
DIMENSIONS = 1024
MODEL_VERSION = f"{MODEL_ID}@{MODEL_REVISION}:cls:normalized-f32:8192:v1"
MAX_INDEX_BYTES = 128 * 1024 * 1024


class EmbeddingUnavailable(Exception):
    def __init__(self, status: Literal["model_unavailable", "model_timeout", "model_busy"]):
        self.status = status
        super().__init__(status)


def checked_vectors(vectors: list[list[float]], count: int) -> None:
    if len(vectors) != count:
        raise ValueError("Embedding count mismatch")
    for vector in vectors:
        if len(vector) != DIMENSIONS or not all(math.isfinite(x) for x in vector):
            raise ValueError("Embedding dimensions or values invalid")
        if abs(sum(x * x for x in vector) - 1) > 0.001:
            raise ValueError("Embeddings must be unit normalized")


class EmbeddingOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    vectors: list[list[float]] = Field(min_length=1, max_length=5000)
    encoder_version: str = Field(min_length=1, max_length=200)
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def valid_vectors(self) -> "EmbeddingOutput":
        checked_vectors(self.vectors, len(self.vectors))
        return self


class IndexRow(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    passage_id: str = Field(min_length=1, max_length=100)
    content_hash: str
    vector: list[float]


class EmbeddingIndex(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    format_version: Literal["bge-dense-index-v1"] = "bge-dense-index-v1"
    model_version: str = MODEL_VERSION
    encoder_version: str
    corpus_version: str
    rows: list[IndexRow] = Field(max_length=5000)

    @model_validator(mode="after")
    def valid_rows(self) -> "EmbeddingIndex":
        if len({row.passage_id for row in self.rows}) != len(self.rows):
            raise ValueError("Duplicate index passage")
        checked_vectors([row.vector for row in self.rows], len(self.rows))
        return self

    def matches(self, passages: list[EvidencePassage]) -> bool:
        return (
            self.model_version == MODEL_VERSION
            and self.corpus_version == corpus_version(passages)
            and {row.passage_id: row.content_hash for row in self.rows}
            == {p.passage_id: p.content_hash for p in passages}
        )


def read_index(path: Path) -> EmbeddingIndex:
    with path.open("rb") as file:
        data = file.read(MAX_INDEX_BYTES + 1)
    if len(data) > MAX_INDEX_BYTES:
        raise ValueError("Index too large")
    return EmbeddingIndex.model_validate_json(data)


def write_index(path: Path, index: EmbeddingIndex) -> None:
    data = index.model_dump_json().encode()
    if len(data) > MAX_INDEX_BYTES:
        raise ValueError("Index too large")
    path.parent.mkdir(parents=True, exist_ok=True)
    # A failed build preserves the last complete artifact. No partial index is published.
    descriptor, temporary = tempfile.mkstemp(prefix=".index-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


class Encoder(Protocol):
    async def encode(self, texts: list[str], timeout: float) -> EmbeddingOutput: ...


class LocalBGEEncoder:
    """One bounded subprocess per call; cancellation kills and reaps the CPU worker."""

    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        self.lock = asyncio.Lock()

    async def encode(self, texts: list[str], timeout: float) -> EmbeddingOutput:
        if self.lock.locked():
            raise EmbeddingUnavailable("model_busy")
        async with self.lock:
            if not (self.model_dir / "folkverse-model.json").is_file():
                raise EmbeddingUnavailable("model_unavailable")
            if not texts or len(texts) > 5000 or any(not t or len(t) > 12000 for t in texts):
                raise EmbeddingUnavailable("model_unavailable")
            # Pass only runtime paths/localization. A denylist misses DATABASE_URL and
            # credentials with provider-specific names; the worker needs neither.
            runtime_names = {
                "PATH",
                "HOME",
                "LANG",
                "LC_ALL",
                "LC_CTYPE",
                "TMPDIR",
                "TMP",
                "TEMP",
                "PYTHONPATH",
                "LD_LIBRARY_PATH",
            }
            env = {key: value for key, value in os.environ.items() if key in runtime_names}
            env.update(
                HF_HUB_OFFLINE="1",
                TRANSFORMERS_OFFLINE="1",
                HF_HUB_DISABLE_TELEMETRY="1",
                TOKENIZERS_PARALLELISM="false",
                OMP_NUM_THREADS="2",
            )
            spawning = asyncio.create_task(
                asyncio.create_subprocess_exec(
                    sys.executable,
                    "-m",
                    "folkverse.embedding_worker",
                    str(self.model_dir),
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                    env=env,
                )
            )
            try:
                process = await asyncio.shield(spawning)
            except asyncio.CancelledError:
                try:
                    process = await spawning
                    if process.returncode is None:
                        process.kill()
                    await process.wait()
                except (OSError, ProcessLookupError):
                    pass
                raise
            except OSError:
                raise EmbeddingUnavailable("model_unavailable") from None
            started = time.monotonic()
            try:
                async with asyncio.timeout(timeout):
                    output, _ = await process.communicate(json.dumps({"texts": texts}).encode())
                if process.returncode != 0 or len(output) > MAX_INDEX_BYTES:
                    raise EmbeddingUnavailable("model_unavailable")
                result = EmbeddingOutput.model_validate_json(output)
                checked_vectors(result.vectors, len(texts))
                return result.model_copy(update={"elapsed_ms": (time.monotonic() - started) * 1000})
            except TimeoutError:
                raise EmbeddingUnavailable("model_timeout") from None
            except (ValueError, ValidationError):
                raise EmbeddingUnavailable("model_unavailable") from None
            finally:
                if process.returncode is None:
                    try:
                        process.kill()
                    except ProcessLookupError:
                        pass
                await process.wait()


async def make_index(
    passages: list[EvidencePassage], encoder: Encoder, timeout: float = 600
) -> EmbeddingIndex:
    if not passages or len(passages) > 5000:
        raise ValueError("Expected 1 to 5000 current reviewed passages")
    output = await encoder.encode([p.text for p in passages], timeout)
    checked_vectors(output.vectors, len(passages))
    return EmbeddingIndex(
        encoder_version=output.encoder_version,
        corpus_version=corpus_version(passages),
        rows=[
            IndexRow(passage_id=p.passage_id, content_hash=p.content_hash, vector=vector)
            for p, vector in zip(passages, output.vectors, strict=True)
        ],
    )


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()
