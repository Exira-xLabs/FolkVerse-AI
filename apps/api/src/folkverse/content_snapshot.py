"""Restore an exported, previously reviewed corpus into empty content tables."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

from folkverse.content import KINDS, ContentRow, approved
from folkverse.content_models import ArtifactExhibit, ClaimEvidence, ExhibitRegion, Review


def restore(db: Session, path: Path) -> None:
    document = json.loads(path.read_text())
    if document.get("version") != 1 or document.get("scope") != "Whole Liaoning":
        raise ValueError("Expected a version 1 Whole Liaoning corpus snapshot")
    models: list[tuple[str, Any]] = [
        ("review", Review),
        *list(KINDS.items()),
        ("exhibit_region", ExhibitRegion),
        ("claim_evidence", ClaimEvidence),
        ("artifact_exhibit", ArtifactExhibit),
    ]
    for _, model in models:
        if db.scalar(select(func.count()).select_from(model)):
            raise ValueError("Restore requires empty content tables; existing work is preserved")
    for kind, model in models:
        mapper = inspect(model)
        assert mapper is not None
        columns = {c.key for c in mapper.columns}
        rows = document.get(kind)
        if not isinstance(rows, list):
            raise ValueError(f"Snapshot is missing {kind}")
        for entry in rows:
            if not isinstance(entry, dict) or set(entry) != columns:
                raise ValueError(f"Invalid fields in {kind}")
            values = dict(entry)
            for date_key in ("fetched_at", "reviewed_at"):
                if date_key in values:
                    values[date_key] = datetime.fromisoformat(values[date_key])
            db.add(model(**values))
        db.flush()
    db.expire_all()
    for model in KINDS.values():
        for entry in db.scalars(select(model)):
            row = cast(ContentRow, entry)
            if row.status == "approved" and not approved(db, row):
                raise ValueError("Snapshot review hash or entity identity mismatch")
    # No new reviews are created. Original reviewer/date/hash are preserved.
    # Reference images remain private local files, and missing bytes stay ineligible.
