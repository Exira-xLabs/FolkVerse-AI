"""Owned, session-scoped digital learning routes over strictly published exhibits.

A journey stores the visitor's explicit preferences plus the ordered exhibit IDs that were
selected deterministically at write time. It never stores exhibit minutes, titles or source
URLs: those are re-resolved from the current published corpus on every read so a withdrawn or
edited exhibit can never be displayed as current.

Stops carry validated reason *codes* (not prose). ``folkverse.journey_explanations`` renders
localized server-authored text from those codes for any requested locale, so a route can be
re-rendered in the other language without another provider call.
"""

from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from folkverse.database import Base

JOURNEY_ID_PREFIX = "jrn_"

# Cascade is declared at the database level so deleting an anonymous session removes its
# routes and stops without a separate application cleanup job. The ORM never needs to load
# children to delete a session.
JOURNEY_OWNER_FK = ForeignKey("anonymous_sessions.id", ondelete="CASCADE")
JOURNEY_STOP_FK = ForeignKey("journeys.id", ondelete="CASCADE")


class Journey(Base):
    __tablename__ = "journeys"
    __table_args__ = (
        CheckConstraint("locale IN ('en','zh-CN')", name="ck_journeys_locale"),
        CheckConstraint("duration_minutes BETWEEN 5 AND 60", name="ck_journeys_duration"),
        CheckConstraint("total_minutes BETWEEN 0 AND 60", name="ck_journeys_total"),
        CheckConstraint("version >= 1", name="ck_journeys_version"),
        CheckConstraint(
            "explanation_status IN ('deterministic','generated','unavailable')",
            name="ck_journeys_explanation_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    owner_session: Mapped[str] = mapped_column(JOURNEY_OWNER_FK, index=True)
    locale: Mapped[str] = mapped_column(String(8))
    interests: Mapped[list[str]] = mapped_column(JSON)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    region_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    novelty_exhibit_ids: Mapped[list[str]] = mapped_column(JSON)
    start_exhibit_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    total_minutes: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer)
    explanation_status: Mapped[str] = mapped_column(String(20))
    notice_codes: Mapped[list[str]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class JourneyStop(Base):
    """One ordered stop of a journey; ``position`` is zero-based within its journey."""

    __tablename__ = "journey_stops"
    __table_args__ = (
        CheckConstraint("position >= 0", name="ck_journey_stops_position"),
    )

    journey_id: Mapped[str] = mapped_column(JOURNEY_STOP_FK, primary_key=True)
    position: Mapped[int] = mapped_column(Integer, primary_key=True)
    # No foreign key to exhibits: a reviewed exhibit can be withdrawn or removed, and the
    # reader must be able to notice that and prune the stop instead of losing it silently.
    exhibit_id: Mapped[str] = mapped_column(String(100), index=True)
    reason_codes: Mapped[list[str]] = mapped_column(JSON)
