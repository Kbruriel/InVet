"""
Esquemas Pydantic para veterinarios
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VeterinarianBase(BaseModel):
    """Base de esquema para veterinarios"""

    model_config = ConfigDict(from_attributes=True)

    name: str
    last_name: str
    specialty: str
    email: str
    phone: Optional[str] = None
    license_number: str  # Matrícula profesional
    is_active: bool = True


class VeterinarianCreate(VeterinarianBase):
    """Esquema para crear un veterinario"""

    branch_id: int


class VeterinarianUpdate(VeterinarianBase):
    """Esquema para actualizar un veterinario"""

    pass


class VeterinarianResponse(VeterinarianBase):
    """Esquema de respuesta para veterinarios"""

    id: int
    branch_id: int
    created_at: datetime
    updated_at: datetime
