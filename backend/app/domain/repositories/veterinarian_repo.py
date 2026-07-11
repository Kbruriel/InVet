"""
Interfaz de repositorio para Veterinarios
"""
from typing import List, Optional

from app.domain.entities.veterinarian import (
    Veterinarian,
    VeterinarianCreate,
    VeterinarianUpdate,
)


class VeterinarianRepository:
    """Interfaz de repositorio para veterinarios"""

    def create_veterinarian(self, veterinarian: VeterinarianCreate) -> Veterinarian:
        raise NotImplementedError

    def get_veterinarian(self, veterinarian_id: int) -> Optional[Veterinarian]:
        raise NotImplementedError

    def get_veterinarians(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Veterinarian]:
        raise NotImplementedError

    def update_veterinarian(
        self, veterinarian_id: int, veterinarian_data: VeterinarianUpdate
    ) -> Optional[Veterinarian]:
        raise NotImplementedError

    def delete_veterinarian(self, veterinarian_id: int) -> bool:
        raise NotImplementedError
