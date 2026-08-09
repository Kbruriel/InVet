"""Entidades para servicios de la clínica."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Service(BaseModel):
    """Entidad de servicio de la clínica.

    Representa un servicio veterinario ofrecido por una clínica.
    El nombre debe ser único dentro de la misma clínica.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
