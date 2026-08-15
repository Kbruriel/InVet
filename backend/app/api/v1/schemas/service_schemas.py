"""Schemas Pydantic para servicios (slice 006)."""

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreateSchema(BaseModel):
    """Schema para crear un servicio."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ..., min_length=1, max_length=200, description="Nombre del servicio"
    )
    description: str | None = Field(
        None, max_length=2000, description="Descripción del servicio"
    )
    price: float = Field(
        ..., gt=0, description="Precio del servicio (debe ser positivo)"
    )
    duration_minutes: int = Field(
        ..., gt=0, description="Duración en minutos (debe ser positivo)"
    )
    is_active: bool = Field(True, description="Estado activo/inactivo")


class ServiceUpdateSchema(BaseModel):
    """Schema para actualizar un servicio."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    price: float | None = Field(None, gt=0)
    duration_minutes: int | None = Field(None, gt=0)
    is_active: bool | None = None


class ServiceReadSchema(BaseModel):
    """Schema de lectura de un servicio."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    name: str
    description: str | None
    price: float
    duration_minutes: int
    is_active: bool


class ServiceListSchema(BaseModel):
    """Schema de lista paginada de servicios."""

    items: list[ServiceReadSchema]
    total: int
    page: int
    size: int
