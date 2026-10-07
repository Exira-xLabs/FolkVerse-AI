"""Pinned offline BGE-M3 artifacts and cancellable, network-free CPU query workers."""

import asyncio
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from functools import lru_cache
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


@lru_cache(maxsize=2)
def _index_revision(path: str, signature: tuple[int, int, int, int]) -> EmbeddingIndex:
    return read_index(Path(path))


def cached_index(path: Path) -> EmbeddingIndex:
    stat = path.stat()
    return _index_revision(
        str(path.resolve()), (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    )


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
                OPENBLAS_NUM_THREADS="2",
                MKL_NUM_THREADS="2",
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


class PersistentBGEEncoder(LocalBGEEncoder):
    """One offline CPU worker, bounded lifetime/cache; no private prompts in process args."""

    def __init__(self, model_dir: Path, cache_size: int = 128, lifetime_seconds: float = 1800):
        super().__init__(model_dir)
        from collections import OrderedDict

        self.process: asyncio.subprocess.Process | None = None
        self.signature: str | None = None
        self.started_at = 0.0
        self.requests = 0
        self.cache_size = max(0, min(cache_size, 128))
        self.lifetime_seconds = min(max(lifetime_seconds, 1), 1800)
        self.cache: OrderedDict[str, EmbeddingOutput] = OrderedDict()

    def model_signature(self) -> str:
        marker = self.model_dir / "folkverse-model.json"
        data = json.loads(marker.read_text())
        if data["model_version"] != MODEL_VERSION or not data["files"]:
            raise ValueError("Model identity mismatch")
        metadata = []
        for name in sorted(data["files"]):
            path = (self.model_dir / name).resolve()
            if not path.is_relative_to(self.model_dir.resolve()):
                raise ValueError("Invalid model path")
            stat = path.stat()
            metadata.append([name, stat.st_ino, stat.st_size, stat.st_mtime_ns])
        return hashlib.sha256(json.dumps([data, metadata], sort_keys=True).encode()).hexdigest()

    async def close(self) -> None:
        process, self.process = self.process, None
        self.cache.clear()
        if process is not None:
            if process.returncode is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            await process.wait()

    async def encode(self, texts: list[str], timeout: float) -> EmbeddingOutput:
        method_started = time.monotonic()
        if not texts or len(texts) > 5000 or any(not t or len(t) > 12000 for t in texts):
            raise EmbeddingUnavailable("model_unavailable")
        try:
            signature = self.model_signature()
        except (OSError, ValueError, KeyError, TypeError):
            await self.close()
            raise EmbeddingUnavailable("model_unavailable") from None
        if signature != self.signature:
            await self.close()
            self.signature = signature
        expired = self.process is not None and (
            time.monotonic() - self.started_at > self.lifetime_seconds
            or self.requests >= 256
            or self.process.returncode is not None
        )
        if expired:
            await self.close()
        key = hashlib.sha256(json.dumps([signature, texts]).encode()).hexdigest()
        if key in self.cache:
            result = self.cache[key]
            self.cache.move_to_end(key)
            return result.model_copy(
                update={"elapsed_ms": (time.monotonic() - method_started) * 1000}
            )
        if self.lock.locked():
            raise EmbeddingUnavailable("model_busy")
        async with self.lock:
            started = time.monotonic()
            try:
                async with asyncio.timeout(timeout):
                    if self.process is None:
                        runtime_names = {
                            "PATH",
                            "HOME",
                            "LANG",
                            "LC_ALL",
                            "LC_CTYPE",
                            "TMPDIR",
                            "TMP",
                            "TEMP",
                            "LD_LIBRARY_PATH",
                        }
                        env = {k: v for k, v in os.environ.items() if k in runtime_names}
                        env.update(
                            HF_HUB_OFFLINE="1",
                            TRANSFORMERS_OFFLINE="1",
                            HF_HUB_DISABLE_TELEMETRY="1",
                            TOKENIZERS_PARALLELISM="false",
                            OMP_NUM_THREADS="2",
                            OPENBLAS_NUM_THREADS="2",
                            MKL_NUM_THREADS="2",
                        )
                        spawning = asyncio.create_task(
                            asyncio.create_subprocess_exec(
                                sys.executable,
                                "-m",
                                "folkverse.embedding_worker",
                                str(self.model_dir),
                                "--persistent",
                                stdin=asyncio.subprocess.PIPE,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.DEVNULL,
                                limit=MAX_INDEX_BYTES + 1,
                                env=env,
                            )
                        )
                        try:
                            self.process = await asyncio.shield(spawning)
                        except asyncio.CancelledError:
                            self.process = await spawning
                            raise
                        self.started_at, self.requests = time.monotonic(), 0
                    process = self.process
                    assert process.stdin is not None and process.stdout is not None
                    process.stdin.write(json.dumps({"texts": texts}).encode() + b"\n")
                    await process.stdin.drain()
                    raw = await process.stdout.readline()
                    if not raw or len(raw) > MAX_INDEX_BYTES:
                        raise ValueError("Invalid worker frame")
                    result = EmbeddingOutput.model_validate_json(raw)
                    checked_vectors(result.vectors, len(texts))
                self.requests += 1
                result = result.model_copy(
                    update={"elapsed_ms": (time.monotonic() - started) * 1000}
                )
                if len(texts) == 1 and self.cache_size:
                    self.cache[key] = result
                    while len(self.cache) > self.cache_size:
                        self.cache.popitem(last=False)
                return result
            except asyncio.CancelledError:
                await asyncio.shield(self.close())
                raise
            except TimeoutError:
                await self.close()
                raise EmbeddingUnavailable("model_timeout") from None
            except (OSError, ValueError, ValidationError, BrokenPipeError):
                await self.close()
                raise EmbeddingUnavailable("model_unavailable") from None
