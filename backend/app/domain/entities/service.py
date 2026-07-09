"""
Entidad Servicio
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Service(BaseModel):
    """Entidad Servicio"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    name: str
    description: Optional[str] = None
    duration: int  # En minutos
    price: float
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class ServiceCreate(BaseModel):
    """Schema para crear un servicio"""
    
    branch_id: int
    name: str
    description: Optional[str] = None
    duration: int  # En minutos
    price: float
    is_active: bool = True


class ServiceUpdate(BaseModel):
    """Schema para actualizar un servicio"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None