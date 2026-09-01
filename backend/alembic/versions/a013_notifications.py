"""add notifications table

Revision ID: a013
Revises: a012
Create Date: 2026-08-27 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a013"
down_revision: str | None = "a012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear tabla notifications y constraint unico para dedup (slice BE-013)."""
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "clinic_id",
            sa.Integer(),
            sa.ForeignKey("clinics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("subject", sa.String(2048), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("ref_type", sa.String(50), nullable=True),
        sa.Column("ref_id", sa.Integer(), nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_index(
        "uq_notifications_dedup",
        "notifications",
        ["user_id", "event_type", "ref_type", "ref_id"],
        unique=True,
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index(
        "ix_notifications_is_read", "notifications", ["is_read"]
    )


def downgrade() -> None:
    """Eliminar tabla notifications sin afectar otras tablas."""
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("uq_notifications_dedup", table_name="notifications")
    op.drop_table("notifications")
