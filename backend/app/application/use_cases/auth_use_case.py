"""Casos de uso para autenticacion."""

from fastapi import HTTPException, status

from app.api.schemas.auth_schemas import AuthProfileResponse, AuthTokenResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.domain.models import User, UserCreate
from app.domain.repositories.user_repository import UserRepository


class AuthUseCase:
    """Orquesta registro, login, refresh y perfil."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> AuthTokenResponse:
        normalized_email = email.lower()
        existing_user = await self.user_repository.get_user_by_email(normalized_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un usuario con ese correo",
            )

        user = await self.user_repository.create_user(
            UserCreate(
                email=normalized_email,
                username=normalized_email,
                password=password,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
            )
        )
        return self._issue_tokens(user)

    async def login(self, *, email: str, password: str) -> AuthTokenResponse:
        user = await self._authenticate_user(email=email, password=password)
        return self._issue_tokens(user)

    async def refresh(self, *, refresh_token: str) -> AuthTokenResponse:
        payload = verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._get_user_from_subject(payload.get("sub"))
        self._ensure_active_user(user)
        return self._issue_tokens(user)

    async def get_profile(self, *, user_id: int) -> AuthProfileResponse:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        return AuthProfileResponse(
            id=user.id,
            email=user.email,
            firstName=user.first_name,
            lastName=user.last_name,
            role=self._resolve_role(user),
        )

    async def _authenticate_user(self, *, email: str, password: str) -> User:
        user = await self.user_repository.get_user_by_email(email.lower())
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales invalidas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self._ensure_active_user(user)
        return user

    async def _get_user_from_subject(self, subject: str | None) -> User:
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id = int(subject)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado para el token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def _ensure_active_user(self, user: User) -> None:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo",
            )

    def _issue_tokens(self, user: User) -> AuthTokenResponse:
        claims = {
            "sub": str(user.id),
            "email": user.email,
            "role": self._resolve_role(user),
        }
        return AuthTokenResponse(
            access_token=create_access_token(claims),
            refresh_token=create_refresh_token(claims),
            token_type="bearer",
        )

    def _resolve_role(self, user: User) -> str:
        return "admin" if user.is_admin else "user"
