"""Entidades para veterinarios."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Veterinarian(BaseModel):
    """Entidad de veterinario.

    Representa un profesional veterinario asociado a una clínica.
    La licencia profesional debe ser única dentro de la misma clínica.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    nombre_completo: str = Field(..., min_length=1, max_length=200)
    licencia_profesional: str = Field(..., min_length=1, max_length=100)
    especialidad: str = Field(..., min_length=1, max_length=200)
    telefono: str | None = Field(None, max_length=30)
    email: EmailStr | None = Field(None)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class VeterinarianServiceAssignment(BaseModel):
    """Entidad de asignación de servicio a veterinario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    veterinarian_id: int
    service_id: int
    clinic_id: int
    assigned_at: datetime
