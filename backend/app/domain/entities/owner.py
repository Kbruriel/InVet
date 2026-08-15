"""Entidades para propietarios y mascotas."""

from __future__ import annotations

from datetime import datetime

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
    telefono: str | None = None
    direccion: str | None = None
    fecha_creacion: datetime


class OwnerCreate(BaseModel):
    """Schema para crear un propietario."""

    nombre: str
    email: EmailStr
    telefono: str | None = None
    direccion: str | None = None


class OwnerUpdate(BaseModel):
    """Schema para actualizar un propietario."""

    nombre: str | None = None
    email: EmailStr | None = None
    telefono: str | None = None
    direccion: str | None = None


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
    peso: float | None = None
    fecha_nacimiento: datetime | None = None


class PetCreate(BaseModel):
    """Schema para crear una mascota."""

    nombre: str
    especie: str
    raza: str
    edad: int
    peso: float | None = None
    fecha_nacimiento: datetime | None = None


class PetUpdate(BaseModel):
    """Schema para actualizar una mascota."""

    nombre: str | None = None
    especie: str | None = None
    raza: str | None = None
    edad: int | None = None
    peso: float | None = None
    fecha_nacimiento: datetime | None = None


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
    motivo: str | None = None
    diagnostico: str | None = None
    veterinario: str | None = None


class PetHistoryListResponse(BaseModel):
    """Respuesta paginada del historial basico de una mascota."""

    items: list[PetHistoryEntry]
    meta: dict
