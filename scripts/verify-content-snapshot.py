"""Verify fresh migrations and snapshot restore in a disposable, owned database."""

import json
import os
import subprocess
import sys
from uuid import uuid4

from folkverse.config import ROOT, Settings
from folkverse.content import counts
from folkverse.content_snapshot import restore
from folkverse.database import make_engine
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

settings = Settings()
owner = make_engine(settings)
name = f"folkverse_phase02_check_{uuid4().hex[:12]}"
created = False
try:
    with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as db:
        db.execute(text(f'CREATE DATABASE "{name}"'))
        created = True
    url = make_url(settings.database_url.get_secret_value()).set(database=name)
    environment = dict(os.environ)
    environment["DATABASE_URL"] = url.render_as_string(hide_password=False)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            "apps/api/alembic.ini",
            "upgrade",
            "head",
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    temporary = make_engine(
        settings.model_copy(
            update={
                "database_url": SecretStr(url.render_as_string(hide_password=False))
            }
        )
    )
    try:
        with Session(temporary) as db:
            restore(db, ROOT / "data/manifests/corpus.json")
            db.commit()
            expected = json.loads((ROOT / "data/manifests/corpus.json").read_text())[
                "counts"
            ]
            assert counts(db) == expected
            try:
                restore(db, ROOT / "data/manifests/corpus.json")
                raise AssertionError("Existing content must be preserved")
            except ValueError as exc:
                assert "empty content tables" in str(exc)
            db.rollback()
            assert counts(db) == expected
            print(
                "PASS: fresh migrations, original review hashes, exact corpus counts, "
                "and refusal to overwrite existing content."
            )
    finally:
        temporary.dispose()
finally:
    if created:
        with owner.connect().execution_options(isolation_level="AUTOCOMMIT") as db:
            db.execute(text(f'DROP DATABASE "{name}"'))
    owner.dispose()
