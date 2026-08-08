"""Schemas pblicos para servicios."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class PublicServiceListDTO(BaseModel):
    """DTO de lista para servicio pblico (sin campos internos)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class PublicServicesPaginatedResponse(BaseModel):
    """Respuesta paginada de listados pblicos."""

    data: list[PublicServiceListDTO]
    pagination: dict[str, int | bool]
