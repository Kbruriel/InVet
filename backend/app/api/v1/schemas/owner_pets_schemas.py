"""Schemas Pydantic para propietarios y mascotas (slice 007)."""

from datetime import UTC, date, datetime, time
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
)


def _coerce_fecha_nacimiento(value: Any) -> datetime | None:
    """Aceptar fechas ISO completas o solo `YYYY-MM-DD`."""
    if value is None or value == "":
        return None

    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)

    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=UTC)

    if isinstance(value, str):
        raw_value = value.strip()
        if not raw_value:
            return None

        if raw_value.endswith("Z"):
            raw_value = raw_value[:-1] + "+00:00"

        try:
            parsed_datetime = datetime.fromisoformat(raw_value)
        except ValueError:
            try:
                parsed_date = date.fromisoformat(raw_value)
            except ValueError as exc:
                raise ValueError(
                    "fecha_nacimiento debe ser una fecha ISO 8601 válida."
                ) from exc
            return datetime.combine(parsed_date, time.min, tzinfo=UTC)

        if parsed_datetime.tzinfo is None:
            parsed_datetime = parsed_datetime.replace(tzinfo=UTC)
        return parsed_datetime

    raise ValueError("fecha_nacimiento debe ser una fecha ISO 8601 válida.")


class OwnerCreateSchema(BaseModel):
    """Schema para crear un propietario."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(
        ..., min_length=1, max_length=200, description="Nombre completo del propietario"
    )
    email: EmailStr = Field(..., description="Correo electrónico del propietario")
    telefono: str | None = Field(
        None, max_length=50, description="Teléfono del propietario"
    )
    direccion: str | None = Field(
        None, max_length=1000, description="Dirección del propietario"
    )


class OwnerUpdateSchema(BaseModel):
    """Schema para actualizar un propietario."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(None, min_length=1, max_length=200)
    email: EmailStr | None = None
    telefono: str | None = Field(None, max_length=50)
    direccion: str | None = Field(None, max_length=1000)


class OwnerReadSchema(BaseModel):
    """Schema de lectura de un propietario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    direccion: str | None
    fecha_creacion: datetime


class OwnerListSchema(BaseModel):
    """Schema de lista paginada de propietarios."""

    items: list[OwnerReadSchema]
    total: int
    page: int
    size: int


class PetCreateSchema(BaseModel):
    """Schema para crear una mascota."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(
        ..., min_length=1, max_length=200, description="Nombre de la mascota"
    )
    especie: str = Field(..., description="Especie (perro, gato, otro)")
    raza: str = Field(
        ..., min_length=1, max_length=100, description="Raza de la mascota"
    )
    edad: int = Field(..., ge=0, le=50, description="Edad en años (0-50)")
    peso: float | None = Field(None, gt=0, le=500, description="Peso en kg (0-500)")
    fecha_nacimiento: datetime | None = Field(
        None,
        description="Fecha de nacimiento (ISO 8601 o YYYY-MM-DD)",
    )

    @field_validator("fecha_nacimiento", mode="before")
    @classmethod
    def _normalize_fecha_nacimiento(cls, value: Any) -> datetime | None:
        return _coerce_fecha_nacimiento(value)


class PetUpdateSchema(BaseModel):
    """Schema para actualizar una mascota."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(None, min_length=1, max_length=200)
    especie: str | None = None
    raza: str | None = Field(None, min_length=1, max_length=100)
    edad: int | None = Field(None, ge=0, le=50)
    peso: float | None = Field(None, gt=0, le=500)
    fecha_nacimiento: datetime | None = None

    @field_validator("fecha_nacimiento", mode="before")
    @classmethod
    def _normalize_fecha_nacimiento(cls, value: Any) -> datetime | None:
        return _coerce_fecha_nacimiento(value)


class PetReadSchema(BaseModel):
    """Schema de lectura de una mascota."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    nombre: str
    especie: str
    raza: str
    edad: int
    peso: float | None
    fecha_nacimiento: datetime | None

    @field_serializer("fecha_nacimiento")
    def _serialize_fecha_nacimiento(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.date().isoformat()


class PetListSchema(BaseModel):
    """Schema de lista paginada de mascotas."""

    items: list[PetReadSchema]
    meta: dict


class PetHistoryEntrySchema(BaseModel):
    """Schema de lectura del historial basico de una mascota."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    pet_id: int
    fecha: datetime | None = None
    motivo: str | None = None
    diagnostico: str | None = None
    veterinario: str | None = None


class PetHistoryListSchema(BaseModel):
    """Schema de lista paginada del historial basico."""

    items: list[PetHistoryEntrySchema]
    meta: dict
