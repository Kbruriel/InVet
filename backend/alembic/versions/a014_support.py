"""add support_tickets and ticket_categories tables for basic support (BE-014)

Revision ID: a014
Revises: a013
Create Date: 2026-08-31

Includes seed of 3 default categories per clinic (AC-014-02).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a014"
down_revision: str | None = "a013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear tablas support_tickets y ticket_categories + seed categorias (BE-014)."""

    # --- Ticket categories table ---
    op.create_table(
        "ticket_categories",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "clinic_id",
            sa.Integer(),
            sa.ForeignKey("clinics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
            default=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_ticket_category_clinic",
        "ticket_categories",
        ["clinic_id", "name"],
    )
    op.create_index(
        "ix_ticket_categories_clinic_id", "ticket_categories", ["clinic_id"]
    )

    # --- Seed: 3 categorías default por clinia existente (AC-014-02) ---
    seed_sql = sa.text(
        """
        INSERT INTO ticket_categories (clinic_id, name, description, active, created_at)
        SELECT c.id, cat.name, cat.desc, true, CURRENT_TIMESTAMP
        FROM clinics c
        CROSS JOIN (
            SELECT 'Fattura' AS name, 'Doubts about billing and payments' AS desc
            UNION ALL
            SELECT 'Comportamiento', 'Animal behaviour questions'
            UNION ALL
            Select 'Veterinaria', 'Vaccination, health plan or general care'
        ) cat
        WHERE NOT EXISTS (
            SELECT 1 FROM ticket_categories tc
            WHERE tc.clinic_id = c.id
              AND tc.name = cat.name
        )
        """
    )
    op.get_bind().execute(seed_sql)

    # --- Support tickets table ---
    op.create_table(
        "support_tickets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="iniciado",
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("ticket_categories.id"),
            nullable=True,
        ),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("owners.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "clinic_id",
            sa.Integer(),
            sa.ForeignKey("clinics.id", ondelete="CASCADE"),
            nullable=False,
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
    op.create_index("ix_support_tickets_owner_id", "support_tickets", ["owner_id"])
    op.create_index("ix_support_tickets_clinic_id", "support_tickets", ["clinic_id"])
    op.create_index("ix_support_tickets_status", "support_tickets", ["status"])


def downgrade() -> None:
    """Eliminar tablas en orden inverso (FK cascade support_tickets -> ticket_categories)."""
    op.drop_table("support_tickets")
    op.drop_table("ticket_categories")
