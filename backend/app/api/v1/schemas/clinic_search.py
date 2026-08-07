"""Schemas para búsquedas de clínicas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClinicSearchResult(BaseModel):
    """Resultado individual de búsqueda de clínicas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str | None
    email: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClinicSearchResponse(BaseModel):
    """Respuesta de búsqueda de clínicas con paginación."""

    model_config = ConfigDict(from_attributes=True)

    data: list[ClinicSearchResult]
    pagination: dict[str, int | bool]


# Schema de respuesta para buscar sucursales (solo para el caso protegido o si queremos extenderlo)
class ClinicSearchByBranchResponse(BaseModel):
    """Respuesta de búsqueda con información completa de clínicas y sus sucursales."""

    model_config = ConfigDict(from_attributes=True)

    clinic_id: int
    clinic_name: str
    branches: list[dict]  # Contendrá la respuesta de BranchPublicProfile
