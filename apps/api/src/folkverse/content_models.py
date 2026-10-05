"""Reviewed cultural content and a separate, rights-controlled artifact catalog."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from folkverse.database import Base


class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(30), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(20))
    reviewer: Mapped[str] = mapped_column(String(200))
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    previous_status: Mapped[str] = mapped_column(String(20))


class Reviewed:
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    review_id: Mapped[str | None] = mapped_column(ForeignKey("reviews.id"), nullable=True)


class Region(Reviewed, Base):
    __tablename__ = "regions"
    __table_args__ = (CheckConstraint("status IN ('draft','approved','rejected','withdrawn')"),)
    names: Mapped[dict[str, str]] = mapped_column(JSON)
    approved_geometry_ref: Mapped[str | None] = mapped_column(Text)


class Source(Reviewed, Base):
    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("institution", "external_id"),)
    institution: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    external_id: Mapped[str] = mapped_column(String(100))
    raw_hash: Mapped[str] = mapped_column(String(64))
    raw_payload: Mapped[str] = mapped_column(Text)
    rights_basis: Mapped[str] = mapped_column(Text)


class Passage(Reviewed, Base):
    __tablename__ = "passages"
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(8))
    locator: Mapped[str] = mapped_column(Text)
    rights_basis: Mapped[str] = mapped_column(Text)
    rights_status: Mapped[str] = mapped_column(String(20), default="pending")
    embedding_version: Mapped[str | None] = mapped_column(String(100))


class Exhibit(Reviewed, Base):
    __tablename__ = "exhibits"
    __table_args__ = (CheckConstraint("estimated_minutes BETWEEN 1 AND 60"),)
    title: Mapped[dict[str, str]] = mapped_column(JSON)
    summary: Mapped[dict[str, str]] = mapped_column(JSON)
    themes: Mapped[list[str]] = mapped_column(JSON)
    estimated_minutes: Mapped[int] = mapped_column(Integer)


class ExhibitRegion(Base):
    __tablename__ = "exhibit_regions"
    __table_args__ = (CheckConstraint("geographic_role IN ('practice','origin','context')"),)
    exhibit_id: Mapped[str] = mapped_column(ForeignKey("exhibits.id"), primary_key=True)
    region_id: Mapped[str] = mapped_column(ForeignKey("regions.id"), primary_key=True)
    geographic_role: Mapped[str] = mapped_column(String(20))


class Claim(Reviewed, Base):
    __tablename__ = "claims"
    exhibit_id: Mapped[str] = mapped_column(ForeignKey("exhibits.id"), index=True)
    text: Mapped[str] = mapped_column(Text)


class ClaimEvidence(Base):
    __tablename__ = "claim_evidence"
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), primary_key=True)
    passage_id: Mapped[str] = mapped_column(ForeignKey("passages.id"), primary_key=True)


class Artifact(Reviewed, Base):
    __tablename__ = "artifacts"
    __table_args__ = (UniqueConstraint("institution", "external_object_id"),)
    institution: Mapped[str] = mapped_column(String(200))
    external_object_id: Mapped[str] = mapped_column(String(100))
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    catalog_title: Mapped[str] = mapped_column(Text)
    catalog_date: Mapped[str] = mapped_column(Text)
    medium: Mapped[str] = mapped_column(Text)
    origin: Mapped[dict[str, Any]] = mapped_column(JSON)
    current_location: Mapped[str] = mapped_column(Text)


class Media(Reviewed, Base):
    __tablename__ = "media"
    __table_args__ = (UniqueConstraint("source_id", "url"),)
    source_id: Mapped[str] = mapped_column(ForeignKey("sources.id"), index=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="reference")
    url: Mapped[str] = mapped_column(Text)
    hash: Mapped[str | None] = mapped_column(String(64))
    storage_key: Mapped[str | None] = mapped_column(Text)
    rights_code: Mapped[str] = mapped_column(String(30))
    rights_status: Mapped[str] = mapped_column(String(20), default="pending")
    rights_evidence: Mapped[dict[str, Any]] = mapped_column(JSON)


class ArtifactExhibit(Base):
    __tablename__ = "artifact_exhibits"
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"), primary_key=True)
    exhibit_id: Mapped[str] = mapped_column(ForeignKey("exhibits.id"), primary_key=True)
    evidence_passage_id: Mapped[str] = mapped_column(ForeignKey("passages.id"), primary_key=True)
