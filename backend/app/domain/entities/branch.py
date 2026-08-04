"""Entidades para clínica/sucursal."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Branch(BaseModel):
    """Entidad de sucursal."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    name: str
    description: Optional[str]
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: Optional[str]
    email: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    services: list[Service] = Field(default_factory=list)
    schedules: list[BranchSchedule] = Field(default_factory=list)
    rating_summary: Optional[RatingSummary] = None
    availability_summary: Optional[AvailabilitySummary] = None


class Service(BaseModel):
    """Entidad de servicio."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    name: str
    description: Optional[str]
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


class RatingSummary(BaseModel):
    """Entidad de resumen de calificaciones."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    average_rating: float
    total_reviews: int
    review_distribution: Optional[str]  # JSON string con distribución de calificaciones
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AvailabilitySummary(BaseModel):
    """Entidad de resumen de disponibilidad."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    is_available: bool
    next_available_time: Optional[datetime]
    availability_type: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


Branch.model_rebuild()
