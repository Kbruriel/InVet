"""Interfaces de repositorios para clínicas."""

from abc import ABC, abstractmethod

from app.domain.entities.clinic import Clinic


class ClinicRepository(ABC):
    """Interface para el repositorio de clínicas."""

    @abstractmethod
    async def search_clinics(
        self,
        location: str | None = None,
        service_type: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Clinic]:
        """Buscar clínicas según criterios especificados."""
        pass

    @abstractmethod
    async def get_clinic_count(
        self, location: str | None = None, service_type: str | None = None
    ) -> int:
        """Obtener el número total de clínicas que coinciden con los criterios."""
        pass

    @abstractmethod
    async def get_clinic_by_id(self, clinic_id: int) -> Clinic | None:
        """Obtener una clínica por ID o None si no existe."""
        pass

    # --- CRUD administrativo (BE-005) ---

    @abstractmethod
    async def create_clinic(self, clinic: Clinic) -> Clinic:
        """Crear una nueva clínica. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    async def update_clinic(self, clinic_id: int, data: dict) -> Clinic | None:
        """Actualizar campos de una clínica existente. Retorna None si no existe."""
        pass

    @abstractmethod
    async def deactivate_clinic(self, clinic_id: int) -> Clinic | None:
        """Inactivar una clínica por ID. Retorna None si no existe."""
        pass

    @abstractmethod
    async def activate_clinic(self, clinic_id: int) -> Clinic | None:
        """Reactivar una clínica inactiva por ID. Retorna None si no existe."""
        pass

    @abstractmethod
    async def list_clinics_by_tenant(
        self,
        tenant_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Clinic], int]:
        """Listar clínicas de un tenant con paginación. Retorna (lista, total)."""
        pass
