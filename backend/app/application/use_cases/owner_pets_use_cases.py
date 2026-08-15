"""Casos de uso para propietarios y mascotas (slice 007)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.owner import (
    Owner,
    OwnerCreate,
    OwnerUpdate,
    Pet,
    PetCreate,
    PetHistoryEntry,
    PetUpdate,
)
from app.domain.repositories.owner_repository import OwnerRepository, PetRepository


# ---------------------------------------------------------------------------
# Owner Use Cases
# ---------------------------------------------------------------------------

class CreateOwnerUseCase:
    """Caso de uso para crear un propietario."""

    def __init__(self, repository: OwnerRepository) -> None:
        self.repository = repository

    def execute(self, data: OwnerCreate, user_id: int) -> Owner:
        """Crear un nuevo propietario vinculado a un usuario.

        Args:
            data: Datos del propietario.
            user_id: ID del usuario autenticado.

        Returns:
            Owner con ID asignado.

        Raises:
            ValueError: Si faltan campos obligatorios o datos son inválidos.
        """
        if not data.nombre or not data.nombre.strip():
            raise ValueError("El campo 'nombre' es obligatorio.")

        now = datetime.now(UTC)
        owner = Owner(
            id=0,
            user_id=user_id,
            nombre=data.nombre.strip(),
            email=data.email,
            telefono=data.telefono,
            direccion=data.direccion,
            fecha_creacion=now,
        )
        return self.repository.create_owner(owner)


class GetOwnerUseCase:
    """Caso de uso para obtener un propietario."""

    def __init__(self, repository: OwnerRepository) -> None:
        self.repository = repository

    def execute(self, owner_id: int) -> Owner | None:
        """Obtener un propietario por ID.

        Args:
            owner_id: ID del propietario.

        Returns:
            Owner o None si no existe.
        """
        return self.repository.get_owner_by_id(owner_id)


class GetOwnerByUserIdUseCase:
    """Caso de uso para obtener un propietario por user_id."""

    def __init__(self, repository: OwnerRepository) -> None:
        self.repository = repository

    def execute(self, user_id: int) -> Owner | None:
        """Obtener un propietario vinculado a un usuario.

        Args:
            user_id: ID del usuario.

        Returns:
            Owner o None si no existe.
        """
        return self.repository.get_owner_by_user_id(user_id)


class UpdateOwnerUseCase:
    """Caso de uso para actualizar un propietario."""

    def __init__(self, repository: OwnerRepository) -> None:
        self.repository = repository

    def execute(self, owner_id: int, data: OwnerUpdate) -> Owner | None:
        """Actualizar campos de un propietario existente.

        Args:
            owner_id: ID del propietario.
            data: Campos a actualizar.

        Returns:
            Owner actualizado o None si no existe.
        """
        return self.repository.update_owner(owner_id, data)


# ---------------------------------------------------------------------------
# Pet Use Cases
# ---------------------------------------------------------------------------

class CreatePetUseCase:
    """Caso de uso para crear una mascota."""

    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def execute(self, data: PetCreate, owner_id: int) -> Pet:
        """Crear una nueva mascota vinculada a un propietario.

        Args:
            data: Datos de la mascota.
            owner_id: ID del propietario.

        Returns:
            Pet con ID asignado.

        Raises:
            ValueError: Si faltan campos obligatorios o datos son inválidos.
        """
        if not data.nombre or not data.nombre.strip():
            raise ValueError("El campo 'nombre' es obligatorio.")

        especie = data.especie.lower()
        if especie not in ("perro", "gato", "otro"):
            raise ValueError("La especie debe ser 'perro', 'gato' u 'otro'.")

        if data.edad < 0:
            raise ValueError("La edad debe ser mayor o igual a cero.")

        if data.peso is not None and data.peso <= 0:
            raise ValueError("El peso debe ser mayor a cero.")

        pet = Pet(
            id=0,
            owner_id=owner_id,
            nombre=data.nombre.strip(),
            especie=especie,
            raza=data.raza,
            edad=data.edad,
            peso=data.peso,
            fecha_nacimiento=data.fecha_nacimiento,
        )
        return self.repository.create_pet(pet)


class GetPetUseCase:
    """Caso de uso para obtener una mascota."""

    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def execute(self, pet_id: int) -> Pet | None:
        """Obtener una mascota por ID.

        Args:
            pet_id: ID de la mascota.

        Returns:
            Pet o None si no existe.
        """
        return self.repository.get_pet_by_id(pet_id)


class ListPetsByOwnerUseCase:
    """Caso de uso para listar mascotas de un propietario."""

    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def execute(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Pet], int]:
        """Listar mascotas paginadas de un propietario.

        Args:
            owner_id: ID del propietario.
            page: Número de página.
            size: Tamaño de página.

        Returns:
            Tupla (items, total).
        """
        return self.repository.get_pets_by_owner(owner_id, page, size)


class UpdatePetUseCase:
    """Caso de uso para actualizar una mascota."""

    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def execute(self, pet_id: int, data: PetUpdate) -> Pet | None:
        """Actualizar campos de una mascota existente.

        Args:
            pet_id: ID de la mascota.
            data: Campos a actualizar.

        Returns:
            Pet actualizado o None si no existe.
        """
        return self.repository.update_pet(pet_id, data)


class DeletePetUseCase:
    """Caso de uso para eliminar una mascota."""

    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def execute(self, pet_id: int) -> bool:
        """Eliminar una mascota (soft delete).

        Args:
            pet_id: ID de la mascota.

        Returns:
            True si se eliminó, False si no existe.
        """
        return self.repository.delete_pet(pet_id)


class GetPetHistoryUseCase:
    """Caso de uso para obtener el historial basico de una mascota."""

    def __init__(self, repository: PetRepository) -> None:
        self.repository = repository

    def execute(
        self,
        pet_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[PetHistoryEntry], int]:
        """Obtener historial paginado de una mascota.

        Args:
            pet_id: ID de la mascota.
            page: Número de página.
            size: Tamaño de página.

        Returns:
            Tupla (items, total).
        """
        return self.repository.get_pet_history(pet_id, page, size)
