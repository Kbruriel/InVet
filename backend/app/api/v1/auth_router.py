"""Router v1 para autenticacion."""

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_auth_use_case
from app.api.schemas.auth_schemas import (
    AuthGenericMessageResponse,
    AuthLoginRequest,
    AuthLogoutRequest,
    AuthPasswordResetConfirmRequest,
    AuthPasswordResetRequest,
    AuthProfileResponse,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthTokenResponse,
)
from app.application.use_cases.auth_use_case import AuthUseCase
from app.core.security import get_current_access_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: AuthRegisterRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthTokenResponse:
    """Registra un usuario y devuelve la sesion inicial."""
    return await use_case.register(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login(
    payload: AuthLoginRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthTokenResponse:
    """Autentica por correo y contrasena."""
    return await use_case.login(email=payload.email, password=payload.password)


@router.post("/refresh", response_model=AuthTokenResponse)
async def refresh(
    payload: AuthRefreshRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthTokenResponse:
    """Renueva la sesion usando refresh token."""
    return await use_case.refresh(refresh_token=payload.refresh_token)


@router.get("/me", response_model=AuthProfileResponse)
async def get_me(
    current_user: dict = Depends(get_current_access_user),
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthProfileResponse:
    """Devuelve el perfil del usuario autenticado."""
    return await use_case.get_profile(user_id=current_user["id"])


# --- BE-002: Endpoints para logout y password reset ---


@router.post("/logout", response_model=AuthGenericMessageResponse)
async def logout(
    payload: AuthLogoutRequest,
    current_user: dict = Depends(get_current_access_user),
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthGenericMessageResponse:
    """Cierra la sesion del usuario actual."""
    result = await use_case.logout(
        refresh_token=payload.refresh_token,
        user_id=current_user["id"],
    )
    return AuthGenericMessageResponse(message=result["message"])


@router.post(
    "/password-reset/request",
    response_model=AuthGenericMessageResponse,
)
async def request_password_reset(
    payload: AuthPasswordResetRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthGenericMessageResponse:
    """Solicita recuperacion de password (respuesta generica)."""
    result = await use_case.request_password_reset(email=payload.email)
    return AuthGenericMessageResponse(message=result["message"])


@router.post(
    "/password-reset/confirm",
    response_model=AuthGenericMessageResponse,
)
async def confirm_password_reset(
    payload: AuthPasswordResetConfirmRequest,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> AuthGenericMessageResponse:
    """Confirma la recuperacion de password."""
    result = await use_case.confirm_password_reset(
        reset_token=payload.reset_token,
        new_password=payload.new_password,
    )
    return AuthGenericMessageResponse(message=result["message"])
