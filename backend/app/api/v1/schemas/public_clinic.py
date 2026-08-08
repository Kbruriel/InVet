"""Schemas pblicos para clnicas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicClinicListDTO(BaseModel):
    """DTO de lista para clnica pblica (sin campos internos)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    city: str
    address: str
    rating: float | None = None


class PublicClinicDetailDTO(PublicClinicListDTO):
    """DTO de detalle para clnica pblica (sin campos internos)."""

    state: str | None = None
    country: str | None = None
    phone: str | None = None


class PublicClinicsPaginatedResponse(BaseModel):
    """Respuesta paginada de listados pblicos."""

    data: list[PublicClinicListDTO]
    pagination: dict[str, int | bool]
