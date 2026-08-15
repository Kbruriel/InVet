"""Interfaces de repositorios para propietarios y mascotas."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.owner import (
    Owner,
    OwnerCreate,
    OwnerUpdate,
    Pet,
    PetCreate,
    PetHistoryEntry,
    PetUpdate,
)


class OwnerRepository(ABC):
    """Interface para el repositorio de propietarios."""
    @abstractmethod
    def create_owner(self, owner: Owner) -> Owner:
        """Crear un nuevo propietario. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    def get_owner_by_id(self, owner_id: int) -> Optional[Owner]:
        """Obtener un propietario por ID o None si no existe."""
        pass

    @abstractmethod
    def get_owner_by_user_id(self, user_id: int) -> Optional[Owner]:
        """Obtener un propietario vinculado a un usuario o None si no existe."""
        pass

    @abstractmethod
    def update_owner(self, owner_id: int, data: OwnerUpdate) -> Optional[Owner]:
        """Actualizar campos de un propietario existente. Retorna None si no existe."""
        pass


class PetRepository(ABC):
    """Interface para el repositorio de mascotas."""

    @abstractmethod
    def create_pet(self, pet: Pet) -> Pet:
        """Crear una nueva mascota. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    def get_pet_by_id(self, pet_id: int) -> Optional[Pet]:
        """Obtener una mascota por ID o None si no existe."""
        pass

    @abstractmethod
    def get_pets_by_owner(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Pet], int]:
        """Obtener mascotas paginadas de un propietario. Retorna (items, total)."""
        pass

    @abstractmethod
    def update_pet(self, pet_id: int, data: PetUpdate) -> Optional[Pet]:
        """Actualizar campos de una mascota existente. Retorna None si no existe."""
        pass

    @abstractmethod
    def delete_pet(self, pet_id: int) -> bool:
        """Eliminar una mascota. Retorna True si se eliminó, False si no existe."""
        pass

    @abstractmethod
    def get_pet_history(
        self,
        pet_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[PetHistoryEntry], int]:
        """Obtener historial basico de una mascota paginado."""
        pass
