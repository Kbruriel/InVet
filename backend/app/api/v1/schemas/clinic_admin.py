"""Schemas Pydantic para CRUD administrativo de clinica."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClinicCreateSchema(BaseModel):
    """Schema para crear una clínica."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ..., min_length=1, max_length=200, description="Nombre de la clinica"
    )
    description: str | None = Field(
        None, max_length=2000, description="Descripcion de la clinica"
    )
    address: str = Field(..., min_length=1, max_length=500, description="Direccion")
    city: str = Field(..., min_length=1, max_length=100, description="Ciudad")
    state: str = Field(
        ..., min_length=1, max_length=100, description="Estado/Provincia"
    )
    country: str = Field(..., min_length=1, max_length=100, description="Pais")
    postal_code: str = Field(
        ..., min_length=1, max_length=20, description="Codigo postal"
    )
    phone: str | None = Field(None, max_length=30, description="Telefono")
    email: EmailStr | None = Field(None, description="Email")


class ClinicUpdateSchema(BaseModel):
    """Schema para actualizar una clínica."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    address: str | None = Field(None, min_length=1, max_length=500)
    city: str | None = Field(None, min_length=1, max_length=100)
    state: str | None = Field(None, min_length=1, max_length=100)
    country: str | None = Field(None, min_length=1, max_length=100)
    postal_code: str | None = Field(None, min_length=1, max_length=20)
    phone: str | None = Field(None, max_length=30)
    email: EmailStr | None = Field(None, description="Email")


class ClinicStatusSchema(BaseModel):
    """Schema para cambiar estado de una clínica."""

    model_config = ConfigDict(str_strip_whitespace=True)

    active: bool = Field(..., description="Nuevo estado activo/inactivo")


class ClinicReadSchema(BaseModel):
    """Schema de lectura de una clínica."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str | None
    email: str | None
    is_active: bool


class ClinicListSchema(BaseModel):
    """Schema de lista paginada de clinicas."""

    model_config = ConfigDict(from_attributes=True)

    items: list[ClinicReadSchema]
    total: int
    page: int
    size: int
