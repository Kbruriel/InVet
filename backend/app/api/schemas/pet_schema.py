"""Esquema Pydantic para mascotas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.api.schemas.clinic_schemas import PaginationMeta


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
    has_medical_history: bool = False


class PetCreate(PetBase):
    """Esquema para crear mascotas."""

    pass


class PetUpdate(PetBase):
    """Esquema para actualizar mascotas."""

    pass


class Pet(BaseModel):
    """Esquema para retornar mascotas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedPetsResponse(BaseModel):
    """Respuesta paginada de mascotas."""

    items: list[Pet]
    pagination: PaginationMeta
