"""Entidades para clínica/sucursal."""

from __future__ import annotations

import json
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Branch(BaseModel):
    """Entidad de sucursal."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    name: str
    description: str | None
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
    services: list[Service] = Field(default_factory=list)
    schedules: list[BranchSchedule] = Field(default_factory=list)
    rating_summary: RatingSummary | None = None
    availability_summary: AvailabilitySummary | None = None


class Service(BaseModel):
    """Entidad de servicio."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BranchSchedule(BaseModel):
    """Entidad de horario de sucursal."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    day_of_week: int  # 0=domingo, 1=lunes, ..., 6=sábado
    open_time: str  # Formato HH:MM
    close_time: str  # Formato HH:MM
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("open_time", "close_time", mode="before")
    @classmethod
    def _format_time(cls, value: str | time) -> str:
        if isinstance(value, time):
            return value.strftime("%H:%M")
        return value


class RatingSummary(BaseModel):
    """Entidad de resumen de calificaciones."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    average_rating: float
    total_reviews: int
    review_distribution: str | None  # JSON string con distribución de calificaciones
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("review_distribution", mode="before")
    @classmethod
    def _format_review_distribution(cls, value: str | dict | None) -> str | None:
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return value


class AvailabilitySummary(BaseModel):
    """Entidad de resumen de disponibilidad."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    is_available: bool
    next_available_time: datetime | None
    availability_type: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


Branch.model_rebuild()
