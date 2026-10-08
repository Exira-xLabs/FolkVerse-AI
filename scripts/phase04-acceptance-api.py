"""Disposable PostgreSQL API for reproducible Phase 04 browser/HTTP acceptance.

Uses the configured local PostgreSQL administrator to create/drop only its own database.
Restores the existing reviewed snapshot; no new approval, provider call or serving-data edit.
"""

import argparse
import os
import subprocess
import sys
from uuid import uuid4

import uvicorn
from folkverse.config import ROOT, Settings
from folkverse.content_snapshot import restore
from folkverse.database import make_engine
from folkverse.main import create_app
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    os.chdir(ROOT)
    settings = Settings()
    owner = make_engine(settings)
    name = "folkverse_phase04_acceptance_" + uuid4().hex[:12]
    created = False
    engine = None
    try:
        with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as db:
            db.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        private_url = make_url(settings.database_url.get_secret_value()).set(
            database=name
        )
        url = private_url.render_as_string(hide_password=False)
        migration = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                "apps/api/alembic.ini",
                "upgrade",
                "head",
            ],
            env={**os.environ, "DATABASE_URL": url},
            capture_output=True,
            check=False,
        )
        if migration.returncode:
            raise RuntimeError(
                "Disposable migration failed; credentials and raw output withheld"
            )
        isolated = settings.model_copy(
            update={
                "database_url": SecretStr(url),
                "app_mode": "demo",
                "cookie_secure": False,
                "allowed_origins": ["http://127.0.0.1:3000", "http://127.0.0.1:3002"],
                "deepseek_api_key": None,
                "ollama_api_key": None,
                "daily_ai_budget_usd": 0,
                "daily_ai_budget_unlimited": False,
                "ollama_daily_request_limit": 0,
                "embedding_enabled": False,
            }
        )
        engine = make_engine(isolated)
        with Session(engine) as db:
            restore(db, ROOT / "data/manifests/corpus.json")
            db.commit()
        engine.dispose()
        app = create_app(isolated)
        print(
            "Disposable reviewed-snapshot API ready; provider generation disabled",
            flush=True,
        )
        uvicorn.run(app, host="127.0.0.1", port=args.port)
    finally:
        if engine is not None:
            engine.dispose()
        if created:
            with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as db:
                db.execute(text(f'DROP DATABASE "{name}"'))
        owner.dispose()


if __name__ == "__main__":
    main()
