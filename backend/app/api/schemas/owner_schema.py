"""Esquema Pydantic para propietarios."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class OwnerBase(BaseModel):
    """Esquema base para propietarios."""
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class OwnerCreate(OwnerBase):
    """Esquema para crear propietarios."""
    pass


class OwnerUpdate(OwnerBase):
    """Esquema para actualizar propietarios."""
    pass


class Owner(OwnerBase):
    """Esquema para retornar propietarios."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True