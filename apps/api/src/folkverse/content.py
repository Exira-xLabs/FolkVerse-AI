"""Eligibility is evaluated on every read: no stale published-content cache."""

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from folkverse.config import ROOT
from folkverse.content_models import (
    Artifact,
    Claim,
    ClaimEvidence,
    Exhibit,
    ExhibitRegion,
    Media,
    Passage,
    Region,
    Review,
    Reviewed,
    Source,
)

ContentRow = Region | Source | Passage | Exhibit | Claim | Artifact | Media

KINDS: dict[str, type[ContentRow]] = {
    "region": Region,
    "source": Source,
    "passage": Passage,
    "exhibit": Exhibit,
    "claim": Claim,
    "artifact": Artifact,
    "media": Media,
}


def fingerprint(db: Session, row: Reviewed) -> str:
    mapper = inspect(type(row))
    assert mapper is not None
    values: dict[str, Any] = {
        c.key: getattr(row, c.key)
        for c in mapper.columns
        if c.key not in {"status", "review_id", "embedding_version"}
    }
    if isinstance(row, Exhibit):
        values["regions"] = sorted(
            (r.region_id, r.geographic_role)
            for r in db.scalars(select(ExhibitRegion).where(ExhibitRegion.exhibit_id == row.id))
        )
        values["claims"] = sorted(db.scalars(select(Claim.id).where(Claim.exhibit_id == row.id)))
    if isinstance(row, Claim):
        values["passages"] = sorted(
            db.scalars(select(ClaimEvidence.passage_id).where(ClaimEvidence.claim_id == row.id))
        )
    return hashlib.sha256(
        json.dumps(values, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()


def approved(db: Session, row: Reviewed | None) -> bool:
    if row is None or row.status != "approved" or not row.review_id:
        return False
    review = db.get(Review, row.review_id)
    return bool(
        review
        and review.status == "approved"
        and review.entity_id == row.id
        and KINDS.get(review.entity_type) is type(row)
        and review.content_hash == fingerprint(db, row)
    )


def passage_eligible(db: Session, row: Passage) -> bool:
    return (
        approved(db, row)
        and row.rights_status == "cleared"
        and bool(row.rights_basis)
        and approved(db, db.get(Source, row.source_id))
    )


def exhibit_dependencies(db: Session, row: Exhibit) -> bool:
    regions = list(db.scalars(select(ExhibitRegion).where(ExhibitRegion.exhibit_id == row.id)))
    claims = list(db.scalars(select(Claim).where(Claim.exhibit_id == row.id)))
    if (
        not regions
        or not claims
        or not all(approved(db, db.get(Region, r.region_id)) for r in regions)
    ):
        return False
    for claim in claims:
        passages = list(
            db.scalars(
                select(Passage).join(ClaimEvidence).where(ClaimEvidence.claim_id == claim.id)
            )
        )
        if (
            not approved(db, claim)
            or not passages
            or not all(passage_eligible(db, p) for p in passages)
        ):
            return False
    return True


def published_exhibits(db: Session) -> list[Exhibit]:
    return [
        e
        for e in db.scalars(
            select(Exhibit).where(Exhibit.status == "approved").order_by(Exhibit.id)
        )
        if approved(db, e) and exhibit_dependencies(db, e)
    ]


def verified_media_bytes(row: Media) -> bool:
    if not row.hash or not row.storage_key:
        return False
    path = (ROOT / row.storage_key).resolve()
    if not path.is_relative_to(ROOT / ".local/met/images"):
        return False
    try:
        if path.stat().st_size > 12_000_000:
            return False
        return hashlib.sha256(path.read_bytes()).hexdigest() == row.hash
    except OSError:
        return False


def media_eligible(db: Session, row: Media) -> bool:
    return (
        approved(db, row)
        and row.role == "reference"
        and row.rights_code == "CC0"
        and row.rights_status == "cleared"
        and verified_media_bytes(row)
        and approved(db, db.get(Source, row.source_id))
    )


def published_artifacts(db: Session) -> list[Artifact]:
    result = []
    for row in db.scalars(
        select(Artifact).where(Artifact.status == "approved").order_by(Artifact.id)
    ):
        if (
            approved(db, row)
            and approved(db, db.get(Source, row.source_id))
            and any(
                media_eligible(db, m)
                for m in db.scalars(select(Media).where(Media.artifact_id == row.id))
            )
        ):
            result.append(row)
    return result


def review_record(
    db: Session,
    kind: str,
    identifier: str,
    decision: str,
    reviewer: str,
    notes: str,
    human: bool,
    clear_rights: bool = False,
) -> Review:
    if kind not in KINDS or decision not in {"approved", "rejected", "withdrawn", "draft"}:
        raise ValueError("Unknown record kind or decision")
    if not human or not reviewer.strip() or not notes.strip():
        raise ValueError("A named human reviewer, explicit attestation and notes are required")
    row = cast(ContentRow | None, db.get(KINDS[kind], identifier))
    if row is None:
        raise ValueError("Record not found")
    previous = row.status
    if decision == "approved":
        if isinstance(row, (Passage, Media)):
            if not clear_rights:
                raise ValueError("Approval requires --clear-rights and a documented rights basis")
            if isinstance(row, Media) and (
                row.rights_code != "CC0"
                or not row.hash
                or not verified_media_bytes(row)
                or row.role != "reference"
            ):
                raise ValueError("Media lacks eligible rights or verified image bytes")
            if isinstance(row, Passage) and not row.rights_basis:
                raise ValueError("Passage lacks a rights basis")
            row.rights_status = "cleared"
        if isinstance(row, Source) and not row.rights_basis:
            raise ValueError("Source lacks a documented rights basis")
        if isinstance(row, Exhibit) and not exhibit_dependencies(db, row):
            raise ValueError("Review all regions, sources, passages and claims before publishing")
    review = Review(
        id=f"rev_{uuid4().hex}",
        entity_type=kind,
        entity_id=identifier,
        status=decision,
        previous_status=previous,
        reviewer=reviewer.strip(),
        reviewed_at=datetime.now(UTC),
        notes=notes.strip(),
        content_hash=fingerprint(db, row),
    )
    db.add(review)
    db.flush()
    row.status, row.review_id = decision, review.id
    if isinstance(row, Source) and decision != "approved":
        for passage in db.scalars(select(Passage).where(Passage.source_id == row.id)):
            passage.embedding_version = None
    db.flush()
    return review


def counts(db: Session) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for kind, model in KINDS.items():
        states = {s: 0 for s in ["draft", "approved", "rejected", "withdrawn"]}
        for entry in db.scalars(select(model)):
            row = cast(ContentRow, entry)
            states[row.status] += 1
        result[kind] = states
    result["published_exhibits"] = len(published_exhibits(db))
    result["published_artifacts"] = len(published_artifacts(db))
    result["downloaded_cc0_candidates"] = sum(
        1 for m in db.scalars(select(Media)) if m.rights_code == "CC0" and verified_media_bytes(m)
    )
    return result
