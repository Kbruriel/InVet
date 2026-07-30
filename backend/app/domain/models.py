"""
Modelos del dominio - Entidades y value objects
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# Modelo base para entidades del dominio
class DomainModel(BaseModel):
    """Base model for domain entities"""

    pass


# Entidad de usuario básica
class User(DomainModel):
    id: int
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime


# DTO para creación de usuario (sin contraseñas ni IDs)
class UserCreate(DomainModel):
    email: EmailStr
    username: str
    password: str


# DTO para actualización de usuario
class UserUpdate(DomainModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


# DTO para respuesta de usuario (sin información sensible)
class UserResponse(DomainModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
