"""add reviews and review_responses tables

Revision ID: a012
Revises: a011
Create Date: 2026-08-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a012"
down_revision: str | None = "a011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear tablas de reseñas y respuestas clinicas (slice BE-012)."""
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "appointment_id",
            sa.Integer(),
            sa.ForeignKey("appointments.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "branch_id",
            sa.Integer(),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "clinic_id",
            sa.Integer(),
            sa.ForeignKey("clinics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("owners.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_reviews_appointment_id",
        "reviews",
        ["appointment_id"],
        unique=True,
    )
    op.create_index("ix_reviews_branch_id", "reviews", ["branch_id"])
    op.create_index("ix_reviews_clinic_id", "reviews", ["clinic_id"])
    op.create_index(
        "ix_reviews_created_at", "reviews", ["created_at"]
    )

    op.create_table(
        "review_responses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "review_id",
            sa.Integer(),
            sa.ForeignKey("reviews.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "branch_id",
            sa.Integer(),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("internal_users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_review_responses_review_id",
        "review_responses",
        ["review_id"],
        unique=True,
    )
    op.create_index(
        "ix_review_responses_branch_id",
        "review_responses",
        ["branch_id"],
    )


def downgrade() -> None:
    """Eliminar tablas de reseñas y respuestas clinicas."""
    op.drop_index("ix_review_responses_branch_id", table_name="review_responses")
    op.drop_index("ix_review_responses_review_id", table_name="review_responses")
    op.drop_table("review_responses")
    op.drop_index("ix_reviews_created_at", table_name="reviews")
    op.drop_index("ix_reviews_clinic_id", table_name="reviews")
    op.drop_index("ix_reviews_branch_id", table_name="reviews")
    op.drop_index("ix_reviews_appointment_id", table_name="reviews")
    op.drop_table("reviews")
