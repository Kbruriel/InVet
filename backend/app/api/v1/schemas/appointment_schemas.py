"""Schemas Pydantic para citas médicas (BE-008)."""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AppointmentTypeEnum(str, PyEnum):
    """Tipos de cita."""

    CONSULTATION = "consultation"
    VACCINATION = "vaccination"
    SURGERY = "surgery"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    OTHER = "other"


class AppointmentStatusEnum(str, PyEnum):
    """Estados de cita."""

    PENDING = "pending"
    APPROVED = "approved"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class AppointmentCreateSchema(BaseModel):
    """Schema para crear una cita."""

    model_config = ConfigDict(str_strip_whitespace=True)

    pet_id: int = Field(..., gt=0, description="ID de la mascota")
    veterinarian_id: int | None = Field(None, description="ID del veterinario (opcional)")
    clinic_id: int = Field(..., gt=0, description="ID de la clínica")
    branch_id: int = Field(..., gt=0, description="ID de la sucursal")
    appointment_type: AppointmentTypeEnum = Field(
        default=AppointmentTypeEnum.CONSULTATION, description="Tipo de cita"
    )
    scheduled_start: datetime = Field(
        ..., description="Fecha y hora de inicio programada"
    )
    duration_minutes: int = Field(
        default=30, ge=15, le=480, description="Duración en minutos (mín 15, máx 480)"
    )
    reason: str | None = Field(None, max_length=2000, description="Motivo de la cita")

    @field_validator("scheduled_start")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        """La cita debe ser en el futuro."""
        if v.replace(tzinfo=None) < datetime.now():
            raise ValueError("La fecha de la cita debe ser en el futuro")
        return v


class AppointmentUpdateSchema(BaseModel):
    """Schema para actualizar una cita."""

    model_config = ConfigDict(str_strip_whitespace=True)

    veterinarian_id: int | None = Field(None, description="ID del veterinario")
    scheduled_start: datetime | None = Field(None, description="Nueva fecha programada")
    duration_minutes: int | None = Field(None, ge=15, le=480, description="Nueva duración")
    reason: str | None = Field(None, max_length=2000, description="Motivo de la cita")
    notes: str | None = Field(None, max_length=2000, description="Notas internas")


class StatusTransitionSchema(BaseModel):
    """Schema para transición de estado."""

    model_config = ConfigDict(str_strip_whitespace=True)

    status: AppointmentStatusEnum = Field(..., description="Nuevo estado")
    notes: str | None = Field(None, max_length=2000, description="Notas de la transición")
    scheduled_start: datetime | None = Field(
        None, description="Nueva fecha (solo para reprogramación)"
    )
    duration_minutes: int | None = Field(
        None, ge=15, le=480, description="Nueva duración (solo para reprogramación)"
    )


class AppointmentReadSchema(BaseModel):
    """Schema de lectura de una cita."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    pet_id: int
    veterinarian_id: int | None
    clinic_id: int
    branch_id: int
    appointment_type: AppointmentTypeEnum
    status: AppointmentStatusEnum
    scheduled_start: datetime
    scheduled_end: datetime
    duration_minutes: int
    reason: str | None
    notes: str | None
    created_by: int | None


class AppointmentListSchema(BaseModel):
    """Schema de lista paginada de citas."""

    items: list[AppointmentReadSchema]
    total: int
    page: int
    size: int


class AvailabilitySlotSchema(BaseModel):
    """Schema de slot de disponibilidad."""

    start: datetime
    end: datetime
    is_available: bool = True
    veterinarian_id: int | None = None
    reason: str | None = None


class AvailabilityResponseSchema(BaseModel):
    """Schema de respuesta de disponibilidad."""

    model_config = ConfigDict(str_strip_whitespace=True)

    date: str
    slots: list[AvailabilitySlotSchema]
    meta: dict = Field(default_factory=dict)
