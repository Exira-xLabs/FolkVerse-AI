"""Reusable worker lifecycle, cache/invalidation and credential isolation tests."""

import asyncio
import hashlib
import json

import pytest

from folkverse.guide_embeddings import (
    DIMENSIONS,
    MODEL_VERSION,
    EmbeddingUnavailable,
    PersistentBGEEncoder,
)


def model(tmp_path):
    (tmp_path / "weights").write_bytes(b"fixture")
    (tmp_path / "folkverse-model.json").write_text(
        json.dumps(
            {
                "model_version": MODEL_VERSION,
                "files": {"weights": hashlib.sha256(b"fixture").hexdigest()},
            }
        )
    )


class Input:
    def __init__(self):
        self.writes = []

    def write(self, data):
        self.writes.append(data)

    async def drain(self):
        pass


class Output:
    def __init__(self, block=False, invalid=False):
        self.block, self.invalid = block, invalid

    async def readline(self):
        if self.block:
            await asyncio.Event().wait()
        if self.invalid:
            return b"invalid\n"
        return (
            json.dumps(
                {
                    "vectors": [[float(i == 0) for i in range(DIMENSIONS)]],
                    "encoder_version": "synthetic",
                    "elapsed_ms": 1.0,
                }
            ).encode()
            + b"\n"
        )


class Process:
    def __init__(self, **kwargs):
        self.stdin, self.stdout = Input(), Output(**kwargs)
        self.returncode = None
        self.reaped = False

    def kill(self):
        self.returncode = -9

    async def wait(self):
        self.reaped = True


def test_reuse_cache_invalidation_lifetime_and_clean_shutdown(tmp_path, monkeypatch):
    model(tmp_path)
    processes = []

    async def spawn(*args, **kwargs):
        assert "private" not in str(args)
        assert "DEEPSEEK_API_KEY" not in kwargs["env"] and "DATABASE_URL" not in kwargs["env"]
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        assert "--persistent" in args
        process = Process()
        processes.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fixture_secret")
    monkeypatch.setenv("DATABASE_URL", "fixture")

    async def run():
        encoder = PersistentBGEEncoder(tmp_path, cache_size=1)
        await encoder.encode(["private first"], 1)
        await encoder.encode(["private first"], 1)
        assert len(processes) == 1 and len(processes[0].stdin.writes) == 1
        await encoder.encode(["private second"], 1)
        await encoder.encode(["private first"], 1)
        assert len(processes[0].stdin.writes) == 3  # LRU bound evicted first vector.
        (tmp_path / "weights").write_bytes(b"different file")
        await encoder.encode(["private first"], 1)
        assert len(processes) == 2 and processes[0].reaped
        encoder.requests = 256
        await encoder.encode(["private first"], 1)
        assert len(processes) == 3 and processes[1].reaped
        await encoder.close()
        assert processes[-1].reaped and not encoder.cache

    asyncio.run(run())


@pytest.mark.parametrize("failure", ["timeout", "cancel", "invalid", "crash"])
def test_failed_worker_is_reaped_and_next_request_can_restart(tmp_path, monkeypatch, failure):
    model(tmp_path)
    processes = []

    async def spawn(*args, **kwargs):
        p = Process(
            block=failure in {"timeout", "cancel"} and not processes,
            invalid=failure == "invalid" and not processes,
        )
        processes.append(p)
        return p

    monkeypatch.setattr(asyncio, "create_subprocess_exec", spawn)

    async def run():
        encoder = PersistentBGEEncoder(tmp_path)
        if failure == "crash":
            await encoder.encode(["first"], 1)
            processes[0].returncode = 1
        elif failure == "cancel":
            task = asyncio.create_task(encoder.encode(["first"], 1))
            while not processes:
                await asyncio.sleep(0)
            with pytest.raises(EmbeddingUnavailable, match="model_busy"):
                await encoder.encode(["second"], 1)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            with pytest.raises(EmbeddingUnavailable):
                await encoder.encode(["first"], 0.01)
        await encoder.encode(["second"], 1)
        assert len(processes) == 2 and processes[0].reaped
        await encoder.close()
        assert processes[-1].reaped

    asyncio.run(run())
