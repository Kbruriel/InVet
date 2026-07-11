"""
Esquemas Pydantic para usuarios internos
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InternalUserBase(BaseModel):
    """Base de esquema para usuarios internos"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    last_name: str
    email: str
    role: str  # admin, editor
    is_active: bool = True


class InternalUserCreate(InternalUserBase):
    """Esquema para crear un usuario interno"""

    branch_id: int
    password: str  # Contraseña en claro - será hasheada


class InternalUserUpdate(InternalUserBase):
    """Esquema para actualizar un usuario interno"""

    password: Optional[str] = None  # Contraseña en claro - será hasheada


class InternalUserResponse(InternalUserBase):
    """Esquema de respuesta para usuarios internos"""

    id: int
    branch_id: int
    created_at: datetime
    updated_at: datetime
