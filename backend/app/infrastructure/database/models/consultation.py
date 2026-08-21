"""Modelo ORM de consultas medicas para BE-009."""

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Consultation(Base):
    """Modelo de consultas medicas para la base de datos (BE-009)."""

    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    veterinarian_id = Column(Integer, ForeignKey("veterinarians.id"), nullable=True)
    history = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("internal_users.id"), nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relaciones
    appointment = relationship("Appointment", lazy="noload")
    pet = relationship("Pet", lazy="noload")
    veterinarian = relationship("Veterinarian", lazy="noload")
    clinic = relationship("Clinic", lazy="noload")
    branch = relationship("Branch", lazy="noload")

    __table_args__ = (
        # Una sola consulta por cita completada: evita duplicados.
        UniqueConstraint("appointment_id", name="uq_consultation_appointment"),
    )

    def __repr__(self) -> str:
        return f"<Consultation(id={self.id}, appointment_id={self.appointment_id})>"
