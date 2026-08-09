"""Entidades para usuarios internos."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class InternalUser(BaseModel):
    """Entidad de usuario interno.

    Representa un usuario interno vinculado a una cuenta de autenticación (BE-005).
    Puede estar asociado a múltiples sucursales de su clínica.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int = Field(..., ge=1)
    clinic_id: int = Field(..., ge=1)
    nombre: str = Field(..., min_length=1, max_length=200)
    rol: str = Field(..., min_length=1, max_length=50)
    branch_ids: list[int] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
