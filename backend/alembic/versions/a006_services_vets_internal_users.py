"""slice 006: servicios, veterinarios, usuarios internos y asignaciones

Revision ID: a006_services_vets_internal_users
Revises: 
Create Date: 2026-08-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a006_services_vets_internal_users"
down_revision = None  # Adjust if there's a previous migration
branch_labels = ("slice_006",)
depends_on = None


def upgrade() -> None:
    """Crear tablas para slice 006."""
    # Tabla services (actualizada con price y duration_minutes)
    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("clinic_id", sa.Integer(), sa.ForeignKey("clinics.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("clinic_id", "name", name="uq_service_clinic_name"),
    )

    # Tabla veterinarians (actualizada con campos en español)
    op.create_table(
        "veterinarians",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("clinic_id", sa.Integer(), sa.ForeignKey("clinics.id"), nullable=False),
        sa.Column("nombre_completo", sa.String(200), nullable=False),
        sa.Column("licencia_profesional", sa.String(100), nullable=False),
        sa.Column("especialidad", sa.String(200), nullable=False),
        sa.Column("telefono", sa.String(30), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("clinic_id", "licencia_profesional", name="uq_vet_clinic_license"),
    )

    # Tabla internal_users
    op.create_table(
        "internal_users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("clinic_id", sa.Integer(), sa.ForeignKey("clinics.id"), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("rol", sa.String(50), nullable=False),
        sa.Column("branch_ids", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Tabla de asignación many-to-many
    op.create_table(
        "veterinarian_service_assignments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("veterinarian_id", sa.Integer(), sa.ForeignKey("veterinarians.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clinic_id", sa.Integer(), sa.ForeignKey("clinics.id"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("veterinarian_id", "service_id", name="uq_vet_service_assignment"),
    )


def downgrade() -> None:
    """Eliminar tablas de slice 006."""
    op.drop_table("veterinarian_service_assignments")
    op.drop_table("internal_users")
    op.drop_table("veterinarians")
    op.drop_table("services")
