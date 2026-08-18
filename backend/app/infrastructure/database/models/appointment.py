"""Modelo ORM de citas médicas para BE-008."""

from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class _AppointmentStatus(PyEnum):
    """Valores crudos para el enum de estados (solo uso interno de ORM)."""

    PENDING = "pending"
    APPROVED = "approved"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class _AppointmentType(PyEnum):
    """Valores crudos para el enum de tipos (solo uso interno de ORM)."""

    CONSULTATION = "consultation"
    VACCINATION = "vaccination"
    SURGERY = "surgery"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    OTHER = "other"


class Appointment(Base):
    """Modelo de citas médicas para la base de datos (BE-008)."""

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    veterinarian_id = Column(Integer, ForeignKey("veterinarians.id"), nullable=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    appointment_type = Column(
        Enum(
            _AppointmentType,
            name="appointment_type_enum",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=_AppointmentType.CONSULTATION,
    )
    status = Column(
        Enum(
            _AppointmentStatus,
            name="appointment_status_enum",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=_AppointmentStatus.PENDING,
    )
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=30)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("internal_users.id"), nullable=True)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relaciones
    owner = relationship("Owner", lazy="noload")
    pet = relationship("Pet", lazy="noload")
    veterinarian = relationship("Veterinarian", lazy="noload")
    clinic = relationship("Clinic", lazy="noload")
    branch = relationship("Branch", lazy="noload")

    __table_args__ = (
        UniqueConstraint(
            "veterinarian_id",
            "scheduled_start",
            name="uq_vet_appointment_time",
        ),
    )

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, type={self.appointment_type.name}, status={self.status.name})>"
