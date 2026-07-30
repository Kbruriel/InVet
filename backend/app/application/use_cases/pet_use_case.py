"""Casos de uso para mascotas."""

from typing import List, Optional

from app.domain.repositories.pet_repository import PetRepository
from app.infrastructure.database.models.pet import Pet


class PetUseCase:
    """Casos de uso para operaciones CRUD de mascotas."""

    def __init__(self, pet_repository: PetRepository):
        self.pet_repository = pet_repository

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Obtiene una mascota por ID."""
        return self.pet_repository.get_pet(pet_id)

    def get_pets(self, skip: int = 0, limit: int = 100) -> List[Pet]:
        """Obtiene multiples mascotas con paginacion."""
        return self.pet_repository.get_pets(skip, limit)

    def create_pet(self, pet_data: dict) -> Pet:
        """Crea una nueva mascota."""
        return self.pet_repository.create_pet(pet_data)

    def update_pet(self, pet_id: int, pet_data: dict) -> Optional[Pet]:
        """Actualiza una mascota existente."""
        return self.pet_repository.update_pet(pet_id, pet_data)

    def delete_pet(self, pet_id: int) -> bool:
        """Elimina una mascota."""
        pet = self.pet_repository.get_pet(pet_id)
        if pet and getattr(pet, "has_medical_history", False):
            raise ValueError(
                "No se puede eliminar la mascota porque tiene historial medico"
            )
        return self.pet_repository.delete_pet(pet_id)

    def get_pets_by_owner(
        self, owner_id: int, skip: int = 0, limit: Optional[int] = 100
    ) -> List[Pet]:
        """Obtiene mascotas por propietario."""
        return self.pet_repository.get_pets_by_owner(owner_id, skip, limit)
