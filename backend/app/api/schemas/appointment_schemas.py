"""Schemas Pydantic para citas médicas (BE-008)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# --- Request Schemas ---


class AppointmentCreateRequest(BaseModel):
    """Schema para crear una cita desde el frontend."""

    pet_id: int = Field(..., gt=0, description="ID de la mascota")
    veterinarian_id: int | None = Field(
        None, ge=1, description="ID del veterinario asignado (opcional)"
    )
    clinic_id: int = Field(..., gt=0, description="ID de la clínica")
    branch_id: int = Field(..., gt=0, description="ID de la sucursal")
    appointment_type: str = Field(
        ...,
        description="Tipo de cita: consulta_general, vacunacion, control, reemergencia",
    )
    scheduled_start: datetime = Field(
        ..., description="Fecha y hora de inicio (debe estar en el futuro)"
    )
    duration_minutes: int = Field(
        default=30, ge=15, le=120, description="Duración entre 15 y 120 minutos"
    )
    reason: str | None = Field(
        None, max_length=2000, description="Motivo de la cita (opcional)"
    )

    @field_validator("scheduled_start")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        """Validar que la fecha sea en el futuro."""
        from datetime import datetime as dt

        now = dt.now().replace(microsecond=0)
        if v <= now:
            raise ValueError("La fecha de la cita debe ser en el futuro")
        return v


class StatusUpdateRequest(BaseModel):
    """Schema para actualizar el estado de una cita."""

    action: str = Field(
        ...,
        description="Acción: approve, confirm, complete, cancel, no_show",
    )
    notes: str | None = Field(None, max_length=2000)


class RescheduleRequest(BaseModel):
    """Schema para reprogramar una cita."""

    new_start: datetime = Field(
        ..., description="Nueva fecha y hora (debe estar en el futuro)"
    )
    duration_minutes: int | None = Field(None, ge=15, le=120)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("new_start")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        """Validar que la nueva fecha sea en el futuro."""
        from datetime import datetime as dt

        now = dt.now().replace(microsecond=0)
        if v <= now:
            raise ValueError("La nueva fecha debe estar en el futuro")
        return v


class AvailabilityRequest(BaseModel):
    """Schema para consultar disponibilidad."""

    date: str = Field(..., description="Fecha en formato YYYY-MM-DD")
    veterinarian_id: int | None = Field(None, ge=1)
    branch_id: int | None = Field(None, ge=1)


# --- Response Schemas ---


class AppointmentOut(BaseModel):
    """Schema para respuestas de citas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    pet_id: int
    veterinarian_id: int | None
    clinic_id: int
    branch_id: int
    appointment_type: str
    status: str
    scheduled_start: datetime
    scheduled_end: datetime
    duration_minutes: int
    reason: str | None
    notes: str | None
    created_by: int | None
    updated_at: datetime | None


class AppointmentListResponse(BaseModel):
    """Respuesta paginada de citas."""

    items: list[AppointmentOut]
    meta: dict[str, Any] = Field(
        default_factory=lambda: {"total": 0, "page": 1, "page_size": 20}
    )


class SlotOut(BaseModel):
    """Schema para un slot de disponibilidad."""

    start: datetime
    end: datetime
    is_available: bool = True
    veterinarian_id: int | None = None
    reason: str | None = None


class AvailabilityResponse(BaseModel):
    """Respuesta de disponibilidad."""

    date: str
    slots: list[SlotOut]
    meta: dict[str, Any] = Field(default_factory=lambda: {"total_slots": 0})


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje."""

    message: str
    detail: str | None = None
