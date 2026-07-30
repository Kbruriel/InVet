"""
Casos de uso para Veterinarios
"""

from typing import List, Optional

from app.domain.entities.veterinarian import (
    Veterinarian,
    VeterinarianCreate,
    VeterinarianUpdate,
)
from app.domain.repositories.veterinarian_repo import VeterinarianRepository


class VeterinarianUseCase:
    """Casos de uso para gestión de veterinarios"""

    def __init__(self, veterinarian_repository: VeterinarianRepository):
        self.veterinarian_repository = veterinarian_repository

    def create_veterinarian(
        self, veterinarian_data: VeterinarianCreate
    ) -> Veterinarian:
        """Crea un nuevo veterinario"""
        return self.veterinarian_repository.create_veterinarian(veterinarian_data)

    def get_veterinarian(self, veterinarian_id: int) -> Optional[Veterinarian]:
        """Obtiene un veterinario por ID"""
        return self.veterinarian_repository.get_veterinarian(veterinarian_id)

    def get_veterinarians(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Veterinarian]:
        """Obtiene una lista de veterinarios para una sucursal"""
        return self.veterinarian_repository.get_veterinarians(branch_id, skip, limit)

    def update_veterinarian(
        self, veterinarian_id: int, veterinarian_data: VeterinarianUpdate
    ) -> Optional[Veterinarian]:
        """Actualiza un veterinario existente"""
        return self.veterinarian_repository.update_veterinarian(
            veterinarian_id, veterinarian_data
        )

    def delete_veterinarian(self, veterinarian_id: int) -> bool:
        """Elimina un veterinario"""
        return self.veterinarian_repository.delete_veterinarian(veterinarian_id)
