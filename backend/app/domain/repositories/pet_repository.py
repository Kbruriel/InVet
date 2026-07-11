"""Interface de repositorio para mascotas."""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.infrastructure.database.models.pet import Pet


class PetRepository(ABC):
    """Interface para operaciones CRUD de mascotas."""

    @abstractmethod
    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Obtiene una mascota por ID."""
        pass

    @abstractmethod
    def get_pets(self, skip: int = 0, limit: int = 100) -> List[Pet]:
        """Obtiene múltiples mascotas con paginación."""
        pass

    @abstractmethod
    def create_pet(self, pet_data: dict) -> Pet:
        """Crea una nueva mascota."""
        pass

    @abstractmethod
    def update_pet(self, pet_id: int, pet_data: dict) -> Optional[Pet]:
        """Actualiza una mascota existente."""
        pass

    @abstractmethod
    def delete_pet(self, pet_id: int) -> bool:
        """Elimina una mascota."""
        pass

    @abstractmethod
    def get_pets_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Pet]:
        """Obtiene mascotas por propietario."""
        pass
