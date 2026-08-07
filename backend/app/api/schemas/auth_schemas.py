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


# --- BE-002: Schemas para logout y password reset ---


class AuthLogoutRequest(BaseModel):
    """Payload para logout (refresh token opcional)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    refresh_token: str | None = Field(default=None, min_length=1)


class AuthPasswordResetRequest(BaseModel):
    """Payload para solicitar recuperacion de password."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    email: EmailStr


class AuthPasswordResetConfirmRequest(BaseModel):
    """Payload para confirmar recuperacion de password."""

    model_config = ConfigDict(str_strip_whitespace=True)

    reset_token: str = Field(min_length=1)
    new_password: str = Field(min_length=6)


class AuthGenericMessageResponse(BaseModel):
    """Respuesta generica para operaciones que no revelan informacion sensible."""

    message: str = "Se ha procesado su solicitud correctamente."
