"""add consultations table

Revision ID: a009
Revises: a008
Create Date: 2026-08-18 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a009"
down_revision: str | None = "a008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear la tabla consultations para el slice BE-009."""
    op.create_table(
        "consultations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "appointment_id",
            sa.Integer(),
            sa.ForeignKey("appointments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pet_id",
            sa.Integer(),
            sa.ForeignKey("pets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "clinic_id",
            sa.Integer(),
            sa.ForeignKey("clinics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            sa.Integer(),
            sa.ForeignKey("branches.id", ondelete="SET NULL"),
            nullable=False,
        ),
        sa.Column(
            "veterinarian_id",
            sa.Integer(),
            sa.ForeignKey("veterinarians.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("history", sa.Text(), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=False),
        sa.Column("recommendations", sa.Text(), nullable=False),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("internal_users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.UniqueConstraint("appointment_id", name="uq_consultation_appointment"),
    )

    # Indices para consultas frecuentes
    op.create_index("ix_consultations_pet_id", "consultations", ["pet_id"])
    op.create_index("ix_consultations_clinic_id", "consultations", ["clinic_id"])
    op.create_index(
        "ix_consultations_veterinarian_id", "consultations", ["veterinarian_id"]
    )


def downgrade() -> None:
    """Eliminar la tabla consultations."""
    op.drop_index("ix_consultations_veterinarian_id", table_name="consultations")
    op.drop_index("ix_consultations_clinic_id", table_name="consultations")
    op.drop_index("ix_consultations_pet_id", table_name="consultations")
    op.drop_table("consultations")
