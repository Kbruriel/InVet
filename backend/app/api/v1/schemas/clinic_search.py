"""Schemas para búsquedas de clínicas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ClinicSearchResult(BaseModel):
    """Resultado individual de búsqueda de clínicas (DTO público limpio).

    M-003-02: Se eliminaron campos internos: created_at, updated_at, postal_code, email.
    Solo se exponen campos necesarios para la interfaz pública.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    state: str
    country: str
    phone: str | None
    is_active: bool


class ClinicSearchResponse(BaseModel):
    """Respuesta de búsqueda de clínicas con paginación."""

    model_config = ConfigDict(from_attributes=True)

    data: list[ClinicSearchResult]
    pagination: dict[str, int | bool]


# Schema de respuesta para buscar sucursales (solo para el caso protegido o si queremos extenderlo)
class ClinicSearchByBranchResponse(BaseModel):
    """Respuesta de búsqueda con información completa de clínicas y sus sucursales.

    M-003-01: Este schema se usa solo para respuestas protegidas (no públicas).
    """

    model_config = ConfigDict(from_attributes=True)

    clinic_id: int
    clinic_name: str
    branches: list[dict]  # Contendrá la respuesta de BranchPublicProfile
