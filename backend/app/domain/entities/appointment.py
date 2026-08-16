"""Entidad de dominio para citas médicas."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class AppointmentStatus(PyEnum):
    """Estados posibles de una cita."""

    PENDING = "pending"
    APPROVED = "approved"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class AppointmentType(PyEnum):
    """Tipos de cita."""

    CONSULTATION = "consultation"
    VACCINATION = "vaccination"
    SURGERY = "surgery"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    OTHER = "other"


class Appointment(BaseModel):
    """Entidad de cita médica."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    pet_id: int
    veterinarian_id: int | None = None
    clinic_id: int
    branch_id: int
    appointment_type: AppointmentType
    status: AppointmentStatus = AppointmentStatus.PENDING
    scheduled_start: datetime
    scheduled_end: datetime
    duration_minutes: int = 30
    reason: str | None = None
    notes: str | None = None
    created_by: int | None = None
    updated_at: datetime | None = None


class AppointmentCreate(BaseModel):
    """Schema para crear una cita."""

    pet_id: int
    veterinarian_id: int | None = None
    clinic_id: int
    branch_id: int
    appointment_type: AppointmentType
    scheduled_start: datetime
    duration_minutes: int = 30
    reason: str | None = None

    @field_validator("scheduled_start")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        """La cita debe ser en el futuro."""
        if v.replace(tzinfo=None) < datetime.now():
            raise ValueError("La fecha de la cita debe ser en el futuro")
        return v

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Duración mínima de 15 minutos."""
        if v < 15:
            raise ValueError("La duración mínima es 15 minutos")
        return v

    @property
    def scheduled_end(self) -> datetime:
        """Calcula la hora de fin basada en la duración."""
        from datetime import timedelta

        return self.scheduled_start + timedelta(minutes=self.duration_minutes)


class AppointmentUpdate(BaseModel):
    """Schema para actualizar una cita."""

    veterinarian_id: int | None = None
    scheduled_start: datetime | None = None
    duration_minutes: int | None = None
    reason: str | None = None
    notes: str | None = None


class StatusTransition(BaseModel):
    """Schema para transición de estado."""

    model_config = ConfigDict(from_attributes=True)

    status: AppointmentStatus
    notes: str | None = None
    scheduled_start: datetime | None = None
    duration_minutes: int | None = None


class AppointmentListResponse(BaseModel):
    """Respuesta paginada de citas."""

    items: list[Appointment]
    meta: dict


class AvailabilitySlot(BaseModel):
    """Representa un slot de disponibilidad."""

    start: datetime
    end: datetime
    is_available: bool = True
    veterinarian_id: int | None = None
    reason: str | None = None


class AvailabilityResponse(BaseModel):
    """Respuesta de disponibilidad de horarios."""

    date: str
    slots: list[AvailabilitySlot]
    meta: dict
