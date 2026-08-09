"""Interfaz del repositorio de sesiones."""

from abc import ABC, abstractmethod
from typing import Any


class SessionRepository(ABC):
    """Interfaz para el repositorio de sesiones.

    Las implementaciones concretas deben mapear entre DTOs y modelos ORM.
    Esta interfaz no conoce la capa de infraestructura.
    """

    @abstractmethod
    async def create_session(self, session_data: dict[str, Any]) -> dict[str, Any]:
        """Crea una nueva sesion."""
        pass

    @abstractmethod
    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> dict[str, Any] | None:
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
