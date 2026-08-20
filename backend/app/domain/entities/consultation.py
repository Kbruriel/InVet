"""Entidad de dominio para consultas medicas (BE-009)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Consultation(BaseModel):
    """Entidad de consulta medica veterinaria.

    Regla de negocio clave: una consulta esta siempre vinculada a una cita
    (``appointment_id``) que debe estar en estado ``completed``. La creacion
    de la consulta es una accion de solo escritura; este slice no expone
    actualizaciones ni eliminaciones.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    appointment_id: int = Field(..., gt=0)
    pet_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    branch_id: int = Field(..., gt=0)
    veterinarian_id: int | None = None
    history: str = Field(default="", max_length=3000)
    diagnosis: str = Field(..., min_length=1, max_length=10000)
    recommendations: str = Field(default="", max_length=3000)
    created_by: int | None = None
    updated_at: datetime | None = None


class ConsultationCreate(BaseModel):
    """Datos de entrada para crear una consulta."""

    appointment_id: int = Field(..., gt=0)
    pet_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    branch_id: int | None = Field(
        None,
        gt=0,
        description="Sucursal opcional; si falta se deriva desde la cita",
    )
    veterinarian_id: int | None = None
    history: str | None = Field(
        None,
        max_length=3000,
        description="Historia clínica opcional",
    )
    diagnosis: str = Field(..., min_length=1, max_length=2000)
    recommendations: str | None = Field(
        None,
        max_length=3000,
        description="Recomendaciones opcionales",
    )


class ConsultationListResponse(BaseModel):
    """Respuesta paginada de consultas."""

    items: list[Consultation]
    meta: dict
