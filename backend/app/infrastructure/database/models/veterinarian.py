"""Modelo ORM de veterinario para slice 006."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Veterinarian(Base):
    """Modelo de veterinario para la base de datos (slice 006)."""

    __tablename__ = "veterinarians"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    nombre_completo = Column("nombre_completo", String(200), nullable=False)
    licencia_profesional = Column("licencia_profesional", String(100), nullable=False)
    especialidad = Column("especialidad", String(200), nullable=False)
    telefono = Column("telefono", String(30))
    email = Column("email", String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    clinic = relationship("Clinic", lazy="noload", back_populates="veterinarians")

    __table_args__ = (
        UniqueConstraint("clinic_id", "licencia_profesional", name="uq_vet_clinic_license"),
    )

    def __repr__(self) -> str:
        return f"<Veterinarian(id={self.id}, nombre={self.nombre_completo!r})>"
