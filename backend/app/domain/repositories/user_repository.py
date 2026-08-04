"""Interfaz del repositorio de usuarios."""

from abc import ABC, abstractmethod

from app.domain.models import User, UserCreate, UserUpdate


class UserRepository(ABC):
    """Interfaz para el repositorio de usuarios."""

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> User | None:
        """Obtiene un usuario por ID."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> User | None:
        """Obtiene un usuario por email."""
        pass

    @abstractmethod
    async def create_user(self, user_create: UserCreate) -> User:
        """Crea un nuevo usuario."""
        pass

    @abstractmethod
    async def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Actualiza un usuario."""
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario."""
        pass

    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista usuarios con paginación."""
        pass
