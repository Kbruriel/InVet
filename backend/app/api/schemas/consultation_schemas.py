"""Schemas Pydantic para consultas médicas (BE-009)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsultationCreate(BaseModel):
    """Schema para crear una consulta médica desde el frontend.

    Reglas:
    - ``appointment_id`` debe referir a una cita en estado ``completed``.
    - ``pet_id`` debe coincidir con la mascota de la cita.
    - ``clinic_id`` es ignorado si el backend lo resuelve del usuario.
    """

    appointment_id: int = Field(..., gt=0, description="ID de la cita completada")
    pet_id: int = Field(..., gt=0, description="ID de la mascota")
    clinic_id: int | None = Field(
        None, gt=0, description="ID de la clínica (opcional; se resuelve del usuario)"
    )
    branch_id: int | None = Field(
        None,
        gt=0,
        description="ID de la sucursal (opcional; puede derivarse de la cita)",
    )
    veterinarian_id: int | None = Field(
        None, ge=1, description="ID del veterinario que atendió (opcional)"
    )
    history: str | None = Field(
        None, max_length=3000, description="Historia clínica opcional"
    )
    diagnosis: str = Field(
        ..., min_length=1, max_length=2000, description="Diagnóstico"
    )
    recommendations: str | None = Field(
        None,
        max_length=3000,
        description="Recomendaciones opcionales",
    )


class ConsultationRead(BaseModel):
    """Schema de respuesta para una consulta médica."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    pet_id: int
    clinic_id: int
    branch_id: int
    veterinarian_id: int | None = None
    history: str
    diagnosis: str
    recommendations: str
    created_by: int | None = None
    updated_at: datetime | None = None


class ConsultationPage(BaseModel):
    """Respuesta paginada de consultas médicas."""

    items: list[ConsultationRead]
    meta: dict
