from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from enum import Enum

class UserRole(str, Enum):
    """Roles de usuario disponibles"""
    ADMIN = "admin"
    VETERINARIAN = "veterinarian" 
    CLIENT = "client"
    STAFF = "staff"

class User(BaseModel):
    """Entidad principal para usuarios del sistema"""
    id: Optional[int] = None
    email: EmailStr
    hashed_password: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        # Para admitir modelos Pydantic como objetos serializables
        orm_mode = True

class UserCreate(BaseModel):
    """Esquema para crear un nuevo usuario"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.CLIENT
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserUpdate(BaseModel):
    """Esquema para actualizar un usuario"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserPublic(BaseModel):
    """Esquema para respuesta pública de usuario (sin datos sensibles)"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

class UserSession(BaseModel):
    """Entidad para sesiones de usuario"""
    id: Optional[int] = None
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    
    class Config:
        orm_mode = True