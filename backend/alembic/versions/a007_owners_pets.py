"""slice 007: propietarios y mascotas

Revision ID: a007_owners_pets
Revises: a006_services_vets_internal_users
Create Date: 2026-08-09
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a007_owners_pets"
down_revision = "a006_services_vets_internal_users"
branch_labels = ("slice_007",)
depends_on = None


def upgrade() -> None:
    """Crear tablas para slice 007 (propietarios y mascotas)."""
    # Tabla owners
    op.create_table(
        "owners",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("clinic_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", name="uq_owner_user_id"),
        sa.UniqueConstraint("email", name="uq_owner_email"),
    )

    # Tabla pets
    op.create_table(
        "pets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("owners.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("species", sa.String(50), nullable=False),
        sa.Column("breed", sa.String(100), nullable=True),
        sa.Column("color", sa.String(50), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("weight", sa.String(20), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Índice para buscar mascotas por owner_id
    op.create_index("ix_pets_owner_id", "pets", ["owner_id"])


def downgrade() -> None:
    """Eliminar tablas de slice 007."""
    op.drop_index("ix_pets_owner_id", table_name="pets")
    op.drop_table("pets")
    op.drop_table("owners")
