"""Casos de uso para propietarios."""
from typing import List, Optional

from app.domain.repositories.owner_repository import OwnerRepository
from app.infrastructure.database.models.owner import Owner


class OwnerUseCase:
    """Casos de uso para operaciones CRUD de propietarios."""

    def __init__(self, owner_repository: OwnerRepository):
        self.owner_repository = owner_repository

    def get_owner(self, owner_id: int) -> Optional[Owner]:
        """Obtiene un propietario por ID."""
        return self.owner_repository.get_owner(owner_id)

    def get_owners(self, skip: int = 0, limit: int = 100) -> List[Owner]:
        """Obtiene múltiples propietarios con paginación."""
        return self.owner_repository.get_owners(skip, limit)

    def create_owner(self, owner_data: dict) -> Owner:
        """Crea un nuevo propietario."""
        # Aquí se podría agregar lógica de validación
        return self.owner_repository.create_owner(owner_data)

    def update_owner(self, owner_id: int, owner_data: dict) -> Optional[Owner]:
        """Actualiza un propietario existente."""
        return self.owner_repository.update_owner(owner_id, owner_data)

    def delete_owner(self, owner_id: int) -> bool:
        """Elimina un propietario."""
        # Aquí se podría agregar lógica de validación para evitar eliminaciones
        # cuando el owner tiene mascotas asociadas
        return self.owner_repository.delete_owner(owner_id)
    
    def get_owners_by_clinic(self, clinic_id: int, skip: int = 0, limit: int = 100) -> List[Owner]:
        """Obtiene propietarios por clínica."""
        return self.owner_repository.get_owners_by_clinic(clinic_id, skip, limit)