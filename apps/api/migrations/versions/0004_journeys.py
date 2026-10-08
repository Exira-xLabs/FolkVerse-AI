"""journeys

Revision ID: 0004_journeys
Revises: 0003_gateway
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_journeys"
down_revision = "0003_gateway"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "journeys",
        sa.Column("id", sa.String(length=40), nullable=False),
        sa.Column("owner_session", sa.String(length=36), nullable=False),
        sa.Column("locale", sa.String(length=8), nullable=False),
        sa.Column("interests", sa.JSON(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("region_id", sa.String(length=100), nullable=True),
        sa.Column("novelty_exhibit_ids", sa.JSON(), nullable=False),
        sa.Column("start_exhibit_id", sa.String(length=100), nullable=True),
        sa.Column("total_minutes", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("explanation_status", sa.String(length=20), nullable=False),
        sa.Column("notice_codes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("locale IN ('en','zh-CN')", name="ck_journeys_locale"),
        sa.CheckConstraint("duration_minutes BETWEEN 5 AND 60", name="ck_journeys_duration"),
        sa.CheckConstraint("total_minutes BETWEEN 0 AND 60", name="ck_journeys_total"),
        sa.CheckConstraint("version >= 1", name="ck_journeys_version"),
        sa.CheckConstraint(
            "explanation_status IN ('deterministic','generated','unavailable')",
            name="ck_journeys_explanation_status",
        ),
        sa.ForeignKeyConstraint(
            ["owner_session"], ["anonymous_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_journeys_owner_session", "journeys", ["owner_session"], unique=False)
    op.create_index("ix_journeys_updated_at", "journeys", ["updated_at"], unique=False)
    op.create_table(
        "journey_stops",
        sa.Column("journey_id", sa.String(length=40), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("exhibit_id", sa.String(length=100), nullable=False),
        sa.Column("reason_codes", sa.JSON(), nullable=False),
        sa.CheckConstraint("position >= 0", name="ck_journey_stops_position"),
        sa.ForeignKeyConstraint(["journey_id"], ["journeys.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("journey_id", "position"),
    )
    op.create_index("ix_journey_stops_exhibit_id", "journey_stops", ["exhibit_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_journey_stops_exhibit_id", table_name="journey_stops")
    op.drop_table("journey_stops")
    op.drop_index("ix_journeys_updated_at", table_name="journeys")
    op.drop_index("ix_journeys_owner_session", table_name="journeys")
    op.drop_table("journeys")
