"""Import short, attributed candidate summaries. Never grants approval."""

import hashlib
import json
from datetime import datetime

from sqlalchemy.orm import Session

from folkverse.config import ROOT
from folkverse.content_models import (
    Claim,
    ClaimEvidence,
    Exhibit,
    ExhibitRegion,
    Passage,
    Region,
    Source,
)


def seed(db: Session) -> None:
    document = json.loads((ROOT / "data/seed/liaoning.json").read_text())
    for region in [document["scope"], *document["cities"]]:
        if db.get(Region, region["id"]) is None:
            db.add(
                Region(
                    id=region["id"],
                    names=region["names"],
                    status="draft",
                    approved_geometry_ref=None,
                )
            )
    for source in document["sources"]:
        if db.get(Source, source["id"]) is None:
            raw = json.dumps(source, sort_keys=True, ensure_ascii=False)
            db.add(
                Source(
                    id=source["id"],
                    institution=source["institution"],
                    title=source["title"],
                    canonical_url=source["url"],
                    fetched_at=datetime.fromisoformat(document["prepared_at"]),
                    external_id=source["external_id"],
                    raw_payload=raw,
                    raw_hash=hashlib.sha256(raw.encode()).hexdigest(),
                    rights_basis=(
                        "Original attributed summaries only; no source images or full text licensed"
                    ),
                    status="draft",
                )
            )
    db.flush()
    for candidate in document["exhibits"]:
        identifier = candidate["id"]
        if db.get(Exhibit, identifier) is not None:
            continue  # Never overwrite human edits or reviews on repeated seeding.
        db.add(
            Exhibit(
                id=identifier,
                title=candidate["title"],
                summary=candidate["summary"],
                themes=candidate["themes"],
                estimated_minutes=3,
                status="draft",
            )
        )
        db.flush()
        for region_id in ("liaoning", candidate["city_id"]):
            db.add(
                ExhibitRegion(
                    exhibit_id=identifier, region_id=region_id, geographic_role="practice"
                )
            )
        claim_id = f"claim-{identifier}"
        db.add(
            Claim(
                id=claim_id, exhibit_id=identifier, text=candidate["summary"]["en"], status="draft"
            )
        )
        for locale in ("en", "zh-CN"):
            pid = f"passage-{identifier}-{locale}"
            db.add(
                Passage(
                    id=pid,
                    source_id=candidate["source_id"],
                    text=candidate["summary"][locale],
                    language=locale,
                    locator=candidate["locator"],
                    rights_basis=(
                        "Original short attributed summary; no source images or full text reused"
                    ),
                    rights_status="pending",
                    status="draft",
                    embedding_version=None,
                )
            )
            db.flush()
            db.add(ClaimEvidence(claim_id=claim_id, passage_id=pid))
    db.flush()
