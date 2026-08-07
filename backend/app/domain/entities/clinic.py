"""Entidades para clínica."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Clinic(BaseModel):
    """Entidad de clínica."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str | None = None
    email: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClinicSearchResult(BaseModel):
    """Resultado individual de búsqueda de clínicas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str | None
    email: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
