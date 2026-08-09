"""Schemas Pydantic para veterinarios (slice 006)."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class VeterinarianCreateSchema(BaseModel):
    """Schema para crear un veterinario."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre_completo: str = Field(..., min_length=1, max_length=200, description="Nombre completo del veterinario")
    licencia_profesional: str = Field(..., min_length=1, max_length=100, description="Licencia profesional")
    especialidad: str = Field(..., min_length=1, max_length=200, description="Especialidad")
    telefono: str | None = Field(None, max_length=30, description="Teléfono")
    email: EmailStr | None = Field(None, description="Email")
    is_active: bool = Field(True, description="Estado activo/inactivo")


class VeterinarianUpdateSchema(BaseModel):
    """Schema para actualizar un veterinario."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre_completo: str | None = Field(None, min_length=1, max_length=200)
    licencia_profesional: str | None = Field(None, min_length=1, max_length=100)
    especialidad: str | None = Field(None, min_length=1, max_length=200)
    telefono: str | None = Field(None, max_length=30)
    email: EmailStr | None = None
    is_active: bool | None = None


class VeterinarianReadSchema(BaseModel):
    """Schema de lectura de un veterinario."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    clinic_id: int
    nombre_completo: str
    licencia_profesional: str
    especialidad: str
    telefono: str | None
    email: str | None
    is_active: bool


class VeterinarianListSchema(BaseModel):
    """Schema de lista paginada de veterinarios."""

    items: list[VeterinarianReadSchema]
    total: int
    page: int
    size: int


class AssignmentSchema(BaseModel):
    """Schema de asignación."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    veterinarian_id: int
    service_id: int
    clinic_id: int
    assigned_at: str  # ISO format string for JSON serialization
