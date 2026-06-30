"""Esquemas Pydantic para clínicas y sucursales."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# Esquema para respuesta pública de una sucursal
class BranchProfileResponse(BaseModel):
    """Esquema de respuesta pública para perfil de sucursal"""
    
    branch: Dict[str, Any]
    services: List[Dict[str, Any]]
    schedules: List[Dict[str, Any]]
    ratings_summary: Dict[str, Any]


# Esquema para horario
class ScheduleResponse(BaseModel):
    """Esquema de horario"""
    id: int
    branch_id: int
    day_of_week: int
    open_time: str
    close_time: str
    is_closed: bool
    created_at: datetime
    updated_at: datetime


# Esquema para servicio
class ServiceResponse(BaseModel):
    """Esquema de servicio"""
    id: int
    branch_id: int
    name: str
    description: Optional[str] = None
    duration: int
    price: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Esquema para calificación
class RatingSummaryResponse(BaseModel):
    """Esquema de resumen de calificaciones"""
    average_rating: float
    total_ratings: int
    rating_distribution: Dict[int, int]


# Esquema para datos completos de una sucursal
class BranchPublicDataResponse(BaseModel):
    """Esquema con información pública básica de la sucursal"""
    id: int
    clinic_id: int
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
