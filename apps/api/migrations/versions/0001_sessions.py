import sqlalchemy as sa
from alembic import op

revision = "0001_sessions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "anonymous_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_anonymous_sessions_expires_at", "anonymous_sessions", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_anonymous_sessions_expires_at", "anonymous_sessions")
    op.drop_table("anonymous_sessions")
    # Other applications may use the extension; leave it intact.
