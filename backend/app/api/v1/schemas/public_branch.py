"""Schemas pblicos para sucursales."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicBranchListDTO(BaseModel):
    """DTO de lista para sucursal pblica (sin campos internos)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    name: str
    description: str | None
    city: str
    address: str


class PublicBranchesPaginatedResponse(BaseModel):
    """Respuesta paginada de listados pblicos."""

    data: list[PublicBranchListDTO]
    pagination: dict[str, int | bool]
