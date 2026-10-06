"""Real PostgreSQL migration, withdrawal and shared admission; disposable DB, no inference."""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from folkverse.config import ROOT, Settings
from folkverse.content_models import Source
from folkverse.content_snapshot import restore
from folkverse.database import make_engine
from folkverse.errors import ApiError
from folkverse.gateway_limits import UsageLedger
from folkverse.guide_harness import SqlEvidenceRepository
from folkverse.guide_retrieval import retrieve


@pytest.fixture
def postgres():
    settings = Settings()
    owner = make_engine(settings)
    name = f"folkverse_guide_check_{uuid4().hex[:12]}"
    engine = None
    created = False
    try:
        with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as db:
            db.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        url = make_url(settings.database_url.get_secret_value()).set(database=name)
        private_url = url.render_as_string(hide_password=False)
        subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
            cwd=ROOT,
            env={**os.environ, "DATABASE_URL": private_url},
            check=True,
            capture_output=True,
        )
        isolated = settings.model_copy(
            update={
                "database_url": SecretStr(private_url),
                "guide_provider": "ollama",
                "ollama_daily_request_limit": 3,
                "model_max_concurrency": 2,
                "model_global_rate_limit_per_minute": 100,
                "model_rate_limit_per_minute": 20,
            }
        )
        engine = make_engine(isolated)
        with Session(engine) as db:
            restore(db, ROOT / "data/manifests/corpus.json")
            db.commit()
        yield engine, isolated
    finally:
        if engine is not None:
            engine.dispose()
        if created:
            with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as db:
                db.execute(text(f'DROP DATABASE "{name}"'))
        owner.dispose()


def test_committed_withdrawal_reaches_new_and_existing_readers(postgres):
    engine, _ = postgres
    repository = SqlEvidenceRepository(engine)
    with Session(engine) as reader:
        before = retrieve(reader, "Fuzhou shadow puppetry", "en")
        assert len(before.passages) == 1
        assert repository.current(before)
        with Session(engine) as editor:
            source = editor.get(Source, before.passages[0].source_id)
            assert source is not None
            # Controlled fault in a disposable copy, never a fabricated human approval.
            source.status = "withdrawn"
            editor.commit()
        assert not repository.current(before)
        assert not repository.current_versions([before.passages[0].passage_id])
        assert not retrieve(reader, "Fuzhou shadow puppetry", "en").passages


def test_postgres_serializes_shared_concurrency_and_counts_failed_attempts(postgres):
    engine, settings = postgres
    ledgers = [UsageLedger(engine, settings) for _ in range(8)]

    def reserve(number):
        try:
            return ledgers[number].reserve(f"isolated-actor-{number}", 0)
        except ApiError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=8) as workers:
        results = list(workers.map(reserve, range(8)))
    admitted = [result for result in results if result.startswith("call_")]
    assert len(admitted) == 2 and results.count("guide_busy") == 6
    ledgers[0].finish(admitted[0], "failed", 1)
    ledgers[1].finish(admitted[1], "cancelled", 1)
    third = ledgers[2].reserve("third-actor", 0)
    ledgers[2].finish(third, "failed", 1)
    with pytest.raises(ApiError) as error:
        ledgers[3].reserve("fourth-actor", 0)
    assert error.value.code == "budget_exhausted"


def test_postgres_rate_limit_shared_across_ledger_instances(postgres):
    engine, settings = postgres
    settings = settings.model_copy(update={"model_rate_limit_per_minute": 1})
    first = UsageLedger(engine, settings)
    second = UsageLedger(engine, settings)
    identifier = first.reserve("same-actor", 0)
    first.finish(identifier, "failed", 1)
    with pytest.raises(ApiError) as error:
        second.reserve("same-actor", 0)
    assert error.value.code == "rate_limited"
