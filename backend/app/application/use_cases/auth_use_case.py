"""Casos de uso para autenticacion."""

from fastapi import HTTPException, status

from app.api.schemas.auth_schemas import AuthProfileResponse, AuthTokenResponse
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.domain.models import User, UserCreate
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.user_repository import UserRepository


class AuthUseCase:
    """Orquesta registro, login, refresh, logout y perfil."""

    def __init__(
        self,
        user_repository: UserRepository,
        session_repository: SessionRepository | None = None,
    ):
        self.user_repository = user_repository
        self.session_repository = session_repository

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

    async def logout(
        self, *, refresh_token: str | None = None, user_id: int
    ) -> dict[str, str]:
        """Revoca la sesion actual o todas las sesiones del usuario."""
        if self.session_repository and refresh_token:
            session = await self.session_repository.get_session_by_refresh_token(
                refresh_token
            )
            if session:
                await self.session_repository.revoke_session(int(session.id))  # type: ignore[arg-type]

        # Revocar todas las sesiones del usuario
        if self.session_repository:
            await self.session_repository.revoke_all_user_sessions(user_id)

        return {"message": "Sesion cerrada correctamente"}

    async def request_password_reset(self, *, email: str) -> dict[str, str]:
        """Solicita recuperacion de password (respuesta generica)."""
        # Siempre responde genericamente para no enumerar correos
        return {
            "message": "Si el correo existe en el sistema, se ha enviado un enlace de recuperacion."
        }

    async def confirm_password_reset(
        self, *, reset_token: str, new_password: str
    ) -> dict[str, str]:
        """Confirma la recuperacion de password."""
        payload = verify_token(reset_token)
        if payload.get("type") != "reset":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de recuperacion invalido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de recuperacion invalido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError) as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de recuperacion invalido",
                headers={"WWW-Authenticate": "Bearer"},
            ) from err

        user = await self.user_repository.get_user_by_id(user_id_int)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de recuperacion invalido",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user.hashed_password = get_password_hash(new_password)
        await self.user_repository.update_user(user.id, None)  # type: ignore[arg-type]
        return {"message": "Password actualizado correctamente"}
