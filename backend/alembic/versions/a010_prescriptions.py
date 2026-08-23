"""add prescriptions tables

Revision ID: a010
Revises: a009
Create Date: 2026-08-21 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a010"
down_revision: str | None = "a009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear las tablas de prescripciones para el slice BE-010."""
    op.create_table(
        "prescriptions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "consultation_id",
            sa.Integer(),
            sa.ForeignKey("consultations.id", ondelete="CASCADE"),
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
            nullable=True,
        ),
        sa.Column(
            "veterinarian_id",
            sa.Integer(),
            sa.ForeignKey("veterinarians.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("diagnosis", sa.Text(), nullable=False),
        sa.Column(
            "treatment_notes", sa.Text(), nullable=False, server_default=sa.text("''")
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("internal_users.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
        sa.UniqueConstraint("consultation_id", name="uq_prescription_consultation"),
    )

    op.create_table(
        "prescription_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "prescription_id",
            sa.Integer(),
            sa.ForeignKey("prescriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("dosage", sa.String(length=200), nullable=True),
        sa.Column("frequency", sa.String(length=200), nullable=True),
        sa.Column("duration", sa.String(length=200), nullable=True),
    )

    op.create_table(
        "prescription_treatments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "prescription_id",
            sa.Integer(),
            sa.ForeignKey("prescriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column(
            "instructions", sa.Text(), nullable=False, server_default=sa.text("''")
        ),
    )

    op.create_table(
        "prescription_reminders",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "prescription_id",
            sa.Integer(),
            sa.ForeignKey("prescriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("due_at", sa.DateTime(), nullable=True),
        sa.Column("note", sa.String(length=1000), nullable=True),
    )

    # Indices para consultas frecuentes
    op.create_index(
        "ix_prescriptions_pet_id",
        "prescriptions",
        ["pet_id"],
    )
    op.create_index(
        "ix_prescriptions_clinic_id",
        "prescriptions",
        ["clinic_id"],
    )
    op.create_index(
        "ix_prescriptions_created_at",
        "prescriptions",
        ["created_at"],
    )


def downgrade() -> None:
    """Eliminar las tablas de prescripciones."""
    op.drop_index("ix_prescriptions_created_at", table_name="prescriptions")
    op.drop_index("ix_prescriptions_clinic_id", table_name="prescriptions")
    op.drop_index("ix_prescriptions_pet_id", table_name="prescriptions")
    op.drop_table("prescription_reminders")
    op.drop_table("prescription_treatments")
    op.drop_table("prescription_items")
    op.drop_table("prescriptions")
