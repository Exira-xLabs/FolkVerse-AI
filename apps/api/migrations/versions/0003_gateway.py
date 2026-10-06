"""Persistent provider admission and content-free usage.

Revision ID: 0003_gateway
Revises: 0002_content
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_gateway"
down_revision = "0002_content"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "gateway_lock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.CheckConstraint("id = 1"),
    )
    op.execute("INSERT INTO gateway_lock (id) VALUES (1)")
    op.create_table(
        "gateway_budgets",
        sa.Column("day", sa.String(10), primary_key=True),
        sa.Column("charged_nano_usd", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("charged_nano_usd >= 0"),
    )
    op.create_table(
        "gateway_attempts",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("day", sa.String(10), nullable=False),
        sa.Column("actor_hash", sa.String(64), nullable=True),
        sa.Column("started_at", sa.Float(), nullable=False),
        sa.Column("lease_until", sa.Float(), nullable=False),
        sa.Column("model", sa.String(40), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("charged_nano_usd", sa.BigInteger(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
    )
    for name in ["day", "actor_hash", "started_at"]:
        op.create_index(f"ix_gateway_attempts_{name}", "gateway_attempts", [name])


def downgrade() -> None:
    op.drop_table("gateway_attempts")
    op.drop_table("gateway_budgets")
    op.drop_table("gateway_lock")
