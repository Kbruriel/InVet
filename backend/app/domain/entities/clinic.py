"""
Entidad Clínica
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Clinic(BaseModel):
    """Entidad Clínica"""
    id: int
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class Branch(BaseModel):
    """Entidad Sucursal"""
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
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class Service(BaseModel):
    """Entidad Servicio"""
    id: int
    branch_id: int
    name: str
    description: Optional[str] = None
    duration: int  # En minutos
    price: float
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class Schedule(BaseModel):
    """Entidad Horario"""
    id: int
    branch_id: int
    day_of_week: int  # 0=Lunes, 6=Domingo
    open_time: str  # Formato HH:MM
    close_time: str  # Formato HH:MM
    is_closed: bool = False
    created_at: datetime
    updated_at: datetime


class Rating(BaseModel):
    """Entidad Calificación"""
    id: int
    branch_id: int
    user_id: int
    rating: int  # 1-5 estrellas
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime