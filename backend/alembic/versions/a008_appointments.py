"""add appointments table

Revision ID: a008
Revises:
Create Date: 2026-01-01 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a008"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear la tabla appointments para el slice BE-008."""
    # Crear enums PostgreSQL inline
    appointment_status_enum = sa.Enum(
        "pending",
        "approved",
        "confirmed",
        "completed",
        "no_show",
        "cancelled",
        "rescheduled",
        name="appointment_status_enum",
        create_type=False,
    )
    appointment_type_enum = sa.Enum(
        "consultation",
        "vaccination",
        "surgery",
        "follow_up",
        "emergency",
        "other",
        name="appointment_type_enum",
        create_type=False,
    )

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("owners.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pet_id",
            sa.Integer(),
            sa.ForeignKey("pets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "veterinarian_id",
            sa.Integer(),
            sa.ForeignKey("veterinarians.id", ondelete="SET NULL"),
            nullable=True,
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
            "appointment_type",
            appointment_type_enum,
            nullable=False,
            server_default="consultation",
        ),
        sa.Column(
            "status", appointment_status_enum, nullable=False, server_default="pending"
        ),
        sa.Column("scheduled_start", sa.DateTime(), nullable=False),
        sa.Column("scheduled_end", sa.DateTime(), nullable=False),
        sa.Column(
            "duration_minutes", sa.Integer(), nullable=False, server_default="30"
        ),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.CheckConstraint(
            "scheduled_end > scheduled_start", name="chk_duration_positive"
        ),
        sa.UniqueConstraint(
            "veterinarian_id", "scheduled_start", name="uq_vet_schedule"
        ),
    )

    # Índices para consultas frecuentes
    op.create_index("ix_appointments_clinic_id", "appointments", ["clinic_id"])
    op.create_index("ix_appointments_branch_id", "appointments", ["branch_id"])
    op.create_index(
        "ix_appointments_veterinarian_id", "appointments", ["veterinarian_id"]
    )
    op.create_index("ix_appointments_owner_id", "appointments", ["owner_id"])
    op.create_index("ix_appointments_pet_id", "appointments", ["pet_id"])
    op.create_index("ix_appointments_status", "appointments", ["status"])
    op.create_index(
        "ix_appointments_scheduled_start", "appointments", ["scheduled_start"]
    )
    op.create_index(
        "ix_appointments_clinic_branch_date",
        "appointments",
        ["clinic_id", "branch_id", "scheduled_start"],
    )


def downgrade() -> None:
    """Eliminar la tabla appointments."""
    op.drop_table("appointments")
