"""Schemas para perfiles públicos de clínica/sucursal."""

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel

# --- Schemas de datos públicos ---


class BranchPublicProfileBase(BaseModel):
    """Base schema para perfil público de sucursal."""

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


class BranchPublicProfile(BranchPublicProfileBase):
    """Schema para perfil público de sucursal."""

    services: list["ServicePublic"]
    schedules: list["BranchSchedulePublic"]
    rating_summary: Optional["RatingSummaryPublic"]
    availability_summary: Optional["AvailabilitySummaryPublic"]

    class Config:
        from_attributes = True


class ServicePublic(BaseModel):
    """Schema para servicio publico."""

    id: int
    name: str
    description: str | None
    is_active: bool

    class Config:
        from_attributes = True


class BranchSchedulePublic(BaseModel):
    """Schema para horario público de sucursal."""

    id: int
    day_of_week: int  # 0=domingo, 1=lunes, ..., 6=sábado
    open_time: time
    close_time: time
    is_active: bool

    class Config:
        from_attributes = True


class RatingSummaryPublic(BaseModel):
    """Schema para resumen de calificaciones público."""

    average_rating: float
    total_reviews: int
    review_distribution: str | None  # JSON string con distribución de calificaciones

    class Config:
        from_attributes = True


class AvailabilitySummaryPublic(BaseModel):
    """Schema para resumen de disponibilidad público."""

    is_available: bool
    next_available_time: datetime | None
    availability_type: str | None

    class Config:
        from_attributes = True


BranchPublicProfile.model_rebuild()
