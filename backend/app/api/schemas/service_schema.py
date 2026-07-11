"""
Esquemas Pydantic para servicios
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    """Base de esquema para servicios"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str] = None
    duration: int  # En minutos
    price: float
    is_active: bool = True


class ServiceCreate(ServiceBase):
    """Esquema para crear un servicio"""

    branch_id: int


class ServiceUpdate(ServiceBase):
    """Esquema para actualizar un servicio"""

    pass


class ServiceResponse(ServiceBase):
    """Esquema de respuesta para servicios"""

    id: int
    branch_id: int
    created_at: datetime
    updated_at: datetime
