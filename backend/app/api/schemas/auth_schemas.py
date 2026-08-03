"""Schemas HTTP para autenticacion."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AuthRegisterRequest(BaseModel):
    """Payload para registro de usuarios."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str = Field(alias="firstName", min_length=1)
    last_name: str = Field(alias="lastName", min_length=1)


class AuthLoginRequest(BaseModel):
    """Payload para login."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=6)


class AuthRefreshRequest(BaseModel):
    """Payload para refresh de token."""

    refresh_token: str = Field(min_length=1)


class AuthTokenResponse(BaseModel):
    """Respuesta para endpoints que emiten tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthProfileResponse(BaseModel):
    """Perfil publico del usuario autenticado."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    email: EmailStr
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    role: str
