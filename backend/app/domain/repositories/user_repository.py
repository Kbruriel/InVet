"""Interfaz del repositorio de usuarios."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models import User, UserCreate, UserUpdate


class UserRepository(ABC):
    """Interfaz para el repositorio de usuarios."""

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email."""
        pass

    @abstractmethod
    async def create_user(self, user_create: UserCreate) -> User:
        """Crea un nuevo usuario."""
        pass

    @abstractmethod
    async def update_user(
        self, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """Actualiza un usuario."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario."""
        pass

    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuarios con paginación."""
        pass
