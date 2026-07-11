"""
Entidad Veterinario
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Veterinarian(BaseModel):
    """Entidad Veterinario"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    branch_id: int
    name: str
    last_name: str
    specialty: str
    email: str
    phone: Optional[str] = None
    license_number: str  # Matrícula profesional
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class VeterinarianCreate(BaseModel):
    """Schema para crear un veterinario"""

    branch_id: int
    name: str
    last_name: str
    specialty: str
    email: str
    phone: Optional[str] = None
    license_number: str  # Matrícula profesional
    is_active: bool = True


class VeterinarianUpdate(BaseModel):
    """Schema para actualizar un veterinario"""

    name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None  # Matrícula profesional
    is_active: Optional[bool] = None
