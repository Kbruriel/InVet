"""Modelo ORM de asignación veterinario-servicio."""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class VeterinarianServiceAssignment(Base):
    """Modelo de asociación many-to-many entre veterinario y servicio."""

    __tablename__ = "veterinarian_service_assignments"

    id = Column(Integer, primary_key=True, index=True)
    veterinarian_id = Column(
        Integer, ForeignKey("veterinarians.id", ondelete="CASCADE"), nullable=False
    )
    service_id = Column(
        Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(UTC))

    veterinarian = relationship("Veterinarian", lazy="noload")
    service = relationship("Service", lazy="noload")

    __table_args__ = (
        UniqueConstraint(
            "veterinarian_id", "service_id", name="uq_vet_service_assignment"
        ),
    )

    def __repr__(self) -> str:
        return f"<Assignment(vet={self.veterinarian_id}, service={self.service_id})>"
