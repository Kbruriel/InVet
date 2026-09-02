"""add payments table

Revision ID: a011
Revises: a010
Create Date: 2026-08-24 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a011"
down_revision: str | None = "a010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

payment_method_enum = sa.Enum(
    "cash",
    "transfer",
    "card",
    "other",
    name="payment_method_enum",
)
payment_status_enum = sa.Enum(
    "paid",
    "cancelled",
    name="payment_status_enum",
)


def upgrade() -> None:
    """Crear la tabla de pagos operativos para el slice BE-011."""
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "appointment_id",
            sa.Integer(),
            sa.ForeignKey("appointments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "service_id",
            sa.Integer(),
            sa.ForeignKey("services.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "clinic_id",
            sa.Integer(),
            sa.ForeignKey("clinics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("method", payment_method_enum, nullable=False, default="cash"),
        sa.Column("amount_received", sa.Integer(), nullable=True),
        sa.Column("change_amount", sa.Integer(), nullable=True),
        sa.Column("status", payment_status_enum, nullable=False, default="paid"),
        sa.Column(
            "paid_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
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
    )

    # Indices para consultas frecuentes
    op.create_index(
        "ix_payments_appointment_id",
        "payments",
        ["appointment_id"],
    )
    op.create_index(
        "ix_payments_service_id",
        "payments",
        ["service_id"],
    )
    op.create_index(
        "ix_payments_clinic_id",
        "payments",
        ["clinic_id"],
    )
    op.create_index(
        "ix_payments_status",
        "payments",
        ["status"],
    )
    op.create_index(
        "ix_payments_created_at",
        "payments",
        ["created_at"],
    )


def downgrade() -> None:
    """Eliminar la tabla de pagos operativos."""
    op.drop_index("ix_payments_created_at", table_name="payments")
    op.drop_index("ix_payments_status", table_name="payments")
    op.drop_index("ix_payments_clinic_id", table_name="payments")
    op.drop_index("ix_payments_service_id", table_name="payments")
    op.drop_index("ix_payments_appointment_id", table_name="payments")
    op.drop_table("payments")
