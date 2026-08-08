"""DTOs pÃºblicos para servicios (capa de aplicaciÃ³n)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicServiceListDTO(BaseModel):
    """DTO de lista para servicio pÃºblico (sin campos internos)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class PublicServicesPaginatedResponse(BaseModel):
    """Respuesta paginada de listados pÃºblicos."""

    data: list[PublicServiceListDTO]
    pagination: dict[str, int | bool]
