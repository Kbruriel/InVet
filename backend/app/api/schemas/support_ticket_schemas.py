"""Schemas Pydantic para soporte basico (BE-014)."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ================================================================== #
# Enum de estados para validacion en schemas
# ================================================================== #


class TicketStatusEnum(str, enum.Enum):
    """Estados permitidos (coincide con dominio)."""

    INICIADO = "iniciado"
    PENDIENTE = "pendiente"
    PROCESO = "proceso"
    COMPLETADO = "completado"
    CERRADO = "cerrado"


# ================================================================== #
# Request Schemas (AC-014-01, AC-014-05)
# ================================================================== #


class TicketCreateRequest(BaseModel):
    """Payload para crear un ticket de soporte."""

    title: str = Field(
        ..., min_length=5, max_length=200, description="Titulo del soporte"
    )
    description: str | None = Field(
        None, max_length=2000, description="Descripcion detallada (opcional)"
    )
    category_id: int | None = Field(
        None, gt=0, description="ID de categoria asignada (opcional)"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) < 5:
            raise ValueError("El titulo debe contener al menos 5 caracteres")
        return v


class TicketStatusUpdateRequest(BaseModel):
    """Payload para cambiar el estado de un ticket."""

    new_status: str = Field(
        ...,
        description="Nuevo estado: iniciado, pendiente, proceso, completado, cerrado",
    )

    @field_validator("new_status")
    @classmethod
    def validate_new_status(cls, v: str) -> str:
        valid_statuses = {"iniciado", "pendiente", "proceso", "completado", "cerrado"}
        if v not in valid_statuses:
            raise ValueError(
                f"Estado invalido. Valores permitidos: {', '.join(sorted(valid_statuses))}"
            )
        return v


# ================================================================== #
# Response Schemas (AC-014-04, AC-014-06)
# ================================================================== #


class CategoryItem(BaseModel):
    """Item de categoria incluido en la respuesta del ticket."""

    id: int
    name: str


class TicketRead(BaseModel):
    """Respuesta completa de un ticket (detalle)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    status: str
    category: CategoryItem | None = None
    category_id: int | None = None
    owner_name: str
    clinic_id: int
    created_at: datetime
    updated_at: datetime


class TicketListItem(BaseModel):
    """Item de respuesta para listados paginados."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: str
    category_name: str | None = None
    owner_name: str
    created_at: datetime


class TicketListResponse(BaseModel):
    """Respuesta paginada de listados de tickets."""

    items: list[TicketListItem]
    meta: dict[str, Any] = Field(
        default_factory=lambda: {"total": 0, "page": 1, "page_size": 20}
    )


class TicketStatusChangeResponse(BaseModel):
    """Respuesta de cambio de estado (AC-014-05)."""

    ticket_id: int
    old_status: str
    new_status: str
