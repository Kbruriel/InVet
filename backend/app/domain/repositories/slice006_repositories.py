"""Interfaces de repositorios para slice 006."""

from abc import ABC, abstractmethod

from app.domain.entities.internal_user import InternalUser
from app.domain.entities.service import Service
from app.domain.entities.veterinarian import (
    Veterinarian,
    VeterinarianServiceAssignment,
)


class ServiceRepository(ABC):
    """Interface para el repositorio de servicios."""

    @abstractmethod
    async def get_service_by_id(
        self, service_id: int, clinic_id: int
    ) -> Service | None:
        """Obtener un servicio por ID y clinic_id. Retorna None si no existe."""
        pass

    @abstractmethod
    async def create_service(self, service: Service) -> Service:
        """Crear un nuevo servicio. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    async def update_service(
        self, service_id: int, clinic_id: int, data: dict
    ) -> Service | None:
        """Actualizar campos de un servicio existente. Retorna None si no existe."""
        pass

    @abstractmethod
    async def deactivate_service(
        self, service_id: int, clinic_id: int
    ) -> Service | None:
        """Inactivar un servicio por ID. Retorna None si no existe."""
        pass

    @abstractmethod
    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[Service], int]:
        """Listar servicios de una clínica con paginación. Retorna (lista, total)."""
        pass

    @abstractmethod
    async def exists_with_name(self, clinic_id: int, name: str) -> bool:
        """Verificar si ya existe un servicio con el mismo nombre en la clínica."""
        pass


class VeterinarianRepository(ABC):
    """Interface para el repositorio de veterinarios."""

    @abstractmethod
    async def get_veterinarian_by_id(
        self, vet_id: int, clinic_id: int
    ) -> Veterinarian | None:
        """Obtener un veterinario por ID y clinic_id. Retorna None si no existe."""
        pass

    @abstractmethod
    async def create_veterinarian(self, veterinarian: Veterinarian) -> Veterinarian:
        """Crear un nuevo veterinario. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    async def update_veterinarian(
        self, vet_id: int, clinic_id: int, data: dict
    ) -> Veterinarian | None:
        """Actualizar campos de un veterinario existente. Retorna None si no existe."""
        pass

    @abstractmethod
    async def deactivate_veterinarian(
        self, vet_id: int, clinic_id: int
    ) -> Veterinarian | None:
        """Inactivar un veterinario por ID. Retorna None si no existe."""
        pass

    @abstractmethod
    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[Veterinarian], int]:
        """Listar veterinarios de una clínica con paginación. Retorna (lista, total)."""
        pass

    @abstractmethod
    async def exists_with_license(self, clinic_id: int, license_number: str) -> bool:
        """Verificar si ya existe un veterinario con la misma licencia en la clínica."""
        pass

    @abstractmethod
    async def get_assigned_services(
        self, vet_id: int, clinic_id: int
    ) -> list[VeterinarianServiceAssignment]:
        """Obtener servicios asignados a un veterinario."""
        pass


class InternalUserRepository(ABC):
    """Interface para el repositorio de usuarios internos."""

    @abstractmethod
    async def get_internal_user_by_id(
        self, user_id: int, clinic_id: int
    ) -> InternalUser | None:
        """Obtener un usuario interno por ID y clinic_id. Retorna None si no existe."""
        pass

    @abstractmethod
    async def create_internal_user(self, internal_user: InternalUser) -> InternalUser:
        """Crear un nuevo usuario interno. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    async def update_internal_user(
        self, user_id: int, clinic_id: int, data: dict
    ) -> InternalUser | None:
        """Actualizar campos de un usuario interno existente. Retorna None si no existe."""
        pass

    @abstractmethod
    async def deactivate_internal_user(
        self, user_id: int, clinic_id: int
    ) -> InternalUser | None:
        """Inactivar un usuario interno por ID. Retorna None si no existe."""
        pass

    @abstractmethod
    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[InternalUser], int]:
        """Listar usuarios internos de una clínica con paginación. Retorna (lista, total)."""
        pass

    @abstractmethod
    async def assign_branch(
        self, user_id: int, clinic_id: int, branch_id: int
    ) -> InternalUser | None:
        """Asignar una sucursal a un usuario interno."""
        pass

    @abstractmethod
    async def unassign_branch(
        self, user_id: int, clinic_id: int, branch_id: int
    ) -> InternalUser | None:
        """Desasignar una sucursal de un usuario interno."""
        pass


class AssignmentRepository(ABC):
    """Interface para el repositorio de asignaciones veterinario-servicio."""

    @abstractmethod
    async def assign_service(
        self, vet_id: int, service_id: int, clinic_id: int
    ) -> VeterinarianServiceAssignment | None:
        """Asignar un servicio a un veterinario. Retorna None si no existe."""
        pass

    @abstractmethod
    async def unassign_service(
        self, vet_id: int, service_id: int, clinic_id: int
    ) -> bool:
        """Desasignar un servicio de un veterinario. Retorna True si se eliminó."""
        pass

    @abstractmethod
    async def get_assignments_by_veterinarian(
        self, vet_id: int, clinic_id: int
    ) -> list[VeterinarianServiceAssignment]:
        """Obtener todas las asignaciones de un veterinario."""
        pass


class AuthServiceRepository(ABC):
    """Interface para validaciones cruzadas con el sistema de autenticación.

    Esta interfaz permite que la capa de aplicación verifique existencia
    de usuarios y sucursales sin importar modelos ORM directamente.
    """

    @abstractmethod
    async def user_exists(self, user_id: int) -> bool:
        """Verificar si un usuario de autenticación existe."""
        pass

    @abstractmethod
    async def branches_belong_to_clinic(
        self, branch_ids: list[int], clinic_id: int
    ) -> list[int]:
        """Verificar que las sucursales pertenecen a la clínica.

        Returns:
            Lista de IDs de sucursales que NO pertenecen a la clínica.
        """
        pass
