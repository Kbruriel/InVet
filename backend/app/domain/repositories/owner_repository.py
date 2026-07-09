"""Interface de repositorio para propietarios."""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.infrastructure.database.models.owner import Owner


class OwnerRepository(ABC):
    """Interface para operaciones CRUD de propietarios."""

    @abstractmethod
    def get_owner(self, owner_id: int) -> Optional[Owner]:
        """Obtiene un propietario por ID."""
        pass

    @abstractmethod
    def get_owners(self, skip: int = 0, limit: int = 100) -> List[Owner]:
        """Obtiene múltiples propietarios con paginación."""
        pass

    @abstractmethod
    def create_owner(self, owner_data: dict) -> Owner:
        """Crea un nuevo propietario."""
        pass

    @abstractmethod
    def update_owner(self, owner_id: int, owner_data: dict) -> Optional[Owner]:
        """Actualiza un propietario existente."""
        pass

    @abstractmethod
    def delete_owner(self, owner_id: int) -> bool:
        """Elimina un propietario."""
        pass

    @abstractmethod
    def get_owners_by_clinic(self, clinic_id: int, skip: int = 0, limit: int = 100) -> List[Owner]:
        """Obtiene propietarios por clínica."""
        pass