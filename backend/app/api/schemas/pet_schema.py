"""Esquema Pydantic para mascotas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PetBase(BaseModel):
    """Esquema base para mascotas."""
    owner_id: int
    name: str
    species: str
    breed: Optional[str] = None
    color: Optional[str] = None
    gender: Optional[str] = None  # 'male', 'female'
    weight: Optional[str] = None
    date_of_birth: Optional[datetime] = None


class PetCreate(PetBase):
    """Esquema para crear mascotas."""
    pass


class PetUpdate(PetBase):
    """Esquema para actualizar mascotas."""
    pass


class Pet(PetBase):
    """Esquema para retornar mascotas."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True