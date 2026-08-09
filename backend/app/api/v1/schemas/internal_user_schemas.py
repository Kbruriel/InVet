"""Schemas Pydantic para usuarios internos (slice 006)."""

from pydantic import BaseModel, ConfigDict, Field


class InternalUserCreateSchema(BaseModel):
    """Schema para crear un usuario interno."""

    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: int = Field(..., ge=1, description="ID del usuario de autenticación (BE-005)")
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del usuario interno")
    rol: str = Field(..., min_length=1, max_length=50, description="Rol del usuario interno")
    branch_ids: list[int] = Field(default_factory=list, description="Lista de IDs de sucursales")
    is_active: bool = Field(True, description="Estado activo/inactivo")


class InternalUserUpdateSchema(BaseModel):
    """Schema para actualizar un usuario interno."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(None, min_length=1, max_length=200)
    rol: str | None = Field(None, min_length=1, max_length=50)
    branch_ids: list[int] | None = None
    is_active: bool | None = None


class InternalUserReadSchema(BaseModel):
    """Schema de lectura de un usuario interno."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    clinic_id: int
    nombre: str
    rol: str
    branch_ids: list[int]
    is_active: bool


class InternalUserListSchema(BaseModel):
    """Schema de lista paginada de usuarios internos."""

    items: list[InternalUserReadSchema]
    total: int
    page: int
    size: int
