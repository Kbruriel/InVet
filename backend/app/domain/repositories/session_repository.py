"""Interfaz del repositorio de sesiones."""

from abc import ABC, abstractmethod

from app.infrastructure.database.models.session import Session


class SessionRepository(ABC):
    """Interfaz para el repositorio de sesiones."""

    @abstractmethod
    async def create_session(self, session: Session) -> Session:
        """Crea una nueva sesion."""
        pass

    @abstractmethod
    async def get_session_by_refresh_token(self, refresh_token: str) -> Session | None:
        """Obtiene una sesion por refresh token."""
        pass

    @abstractmethod
    async def revoke_session(self, session_id: int) -> bool:
        """Revoca una sesion."""
        pass

    @abstractmethod
    async def revoke_all_user_sessions(self, user_id: int) -> int:
        """Revoca todas las sesiones de un usuario."""
        pass
