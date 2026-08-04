"""Schemas para perfiles públicos de clínica/sucursal."""
from typing import Optional, List
from pydantic import BaseModel
from datetime import time, datetime


# --- Schemas de datos públicos ---

class BranchPublicProfileBase(BaseModel):
    """Base schema para perfil público de sucursal."""
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


class BranchPublicProfile(BranchPublicProfileBase):
    """Schema para perfil público de sucursal."""
    services: List['ServicePublic']
    schedules: List['BranchSchedulePublic']
    rating_summary: Optional['RatingSummaryPublic']
    availability_summary: Optional['AvailabilitySummaryPublic']

    class Config:
        from_attributes = True


class ServicePublic(BaseModel):
    """Schema para servicio publico."""
    id: int
    name: str
    description: Optional[str]
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
    review_distribution: Optional[str]  # JSON string con distribución de calificaciones

    class Config:
        from_attributes = True


class AvailabilitySummaryPublic(BaseModel):
    """Schema para resumen de disponibilidad público."""
    is_available: bool
    next_available_time: Optional[datetime]
    availability_type: Optional[str]

    class Config:
        from_attributes = True


BranchPublicProfile.model_rebuild()
