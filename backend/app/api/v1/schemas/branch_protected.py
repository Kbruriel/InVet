"""Schemas para perfiles protegidos de clínica/sucursal."""

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel

# --- Schemas de datos protegidos ---


class BranchProtectedProfileBase(BaseModel):
    """Base schema para perfil protegido de sucursal."""

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


class BranchProtectedProfile(BranchProtectedProfileBase):
    """Schema para perfil protegido de sucursal."""

    services: list["ServiceProtected"]
    schedules: list["BranchScheduleProtected"]
    rating_summary: Optional["RatingSummaryProtected"]
    availability_summary: Optional["AvailabilitySummaryProtected"]

    class Config:
        from_attributes = True


class ServiceProtected(BaseModel):
    """Schema para servicio protegido."""

    id: int
    name: str
    description: str | None
    is_active: bool

    class Config:
        from_attributes = True


class BranchScheduleProtected(BaseModel):
    """Schema para horario protegido de sucursal."""

    id: int
    day_of_week: int  # 0=domingo, 1=lunes, ..., 6=sábado
    open_time: time
    close_time: time
    is_active: bool

    class Config:
        from_attributes = True


class RatingSummaryProtected(BaseModel):
    """Schema para resumen de calificaciones protegido."""

    average_rating: float
    total_reviews: int
    review_distribution: str | None  # JSON string con distribución de calificaciones

    class Config:
        from_attributes = True


class AvailabilitySummaryProtected(BaseModel):
    """Schema para resumen de disponibilidad protegido."""

    is_available: bool
    next_available_time: datetime | None
    availability_type: str | None

    class Config:
        from_attributes = True


BranchProtectedProfile.model_rebuild()
