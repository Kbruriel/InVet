"""Entidades para propietarios y mascotas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner(BaseModel):
    """Entidad de propietario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_creacion: datetime


class OwnerCreate(BaseModel):
    """Schema para crear un propietario."""

    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class OwnerUpdate(BaseModel):
    """Schema para actualizar un propietario."""

    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

class Pet(BaseModel):
    """Entidad de mascota."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    nombre: str
    especie: str  # perro, gato, otro
    raza: str
    edad: int
    peso: Optional[float] = None
    fecha_nacimiento: Optional[datetime] = None


class PetCreate(BaseModel):
    """Schema para crear una mascota."""

    nombre: str
    especie: str
    raza: str
    edad: int
    peso: Optional[float] = None
    fecha_nacimiento: Optional[datetime] = None


class PetUpdate(BaseModel):
    """Schema para actualizar una mascota."""

    nombre: Optional[str] = None
    especie: Optional[str] = None
    raza: Optional[str] = None
    edad: Optional[int] = None
    peso: Optional[float] = None
    fecha_nacimiento: Optional[datetime] = None


class PetListResponse(BaseModel):
    """Respuesta paginada de listado de mascotas."""

    items: list[Pet]
    meta: dict


class PetHistoryEntry(BaseModel):
    """Registro basico del historial de una mascota."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    fecha: datetime | None = None
    motivo: Optional[str] = None
    diagnostico: Optional[str] = None
    veterinario: Optional[str] = None


class PetHistoryListResponse(BaseModel):
    """Respuesta paginada del historial basico de una mascota."""

    items: list[PetHistoryEntry]
    meta: dict
