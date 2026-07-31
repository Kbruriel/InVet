"""
Entidad Usuario Interno
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InternalUser(BaseModel):
    """Entidad Usuario Interno"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    name: str
    last_name: str
    email: str
    role: str  # admin, editor
    password_hash: str  # Contraseña en formato hash
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class InternalUserCreate(BaseModel):
    """Schema para crear un usuario interno"""
    
    branch_id: int
    name: str
    last_name: str
    email: str
    role: str  # admin, editor
    password: str  # Contraseña en claro - será hasheada
    is_active: bool = True


class InternalUserUpdate(BaseModel):
    """Schema para actualizar un usuario interno"""
    
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None  # admin, editor
    password: Optional[str] = None  # Contraseña en claro - será hasheada
    is_active: Optional[bool] = None