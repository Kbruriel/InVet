"""Interfaces de repositorios para clínica/sucursal."""

from abc import ABC, abstractmethod

from app.domain.entities.branch import (
    AvailabilitySummary,
    Branch,
    BranchSchedule,
    RatingSummary,
    Service,
)


class BranchRepository(ABC):
    """Interface para el repositorio de sucursales."""

    @abstractmethod
    async def get_branch_by_id(self, branch_id: int) -> Branch | None:
        """Obtener una sucursal por ID."""
        pass

    @abstractmethod
    async def get_branch_public_profile(self, branch_id: int) -> Branch | None:
        """Obtener perfil público de una sucursal."""
        pass

    @abstractmethod
    async def is_branch_accessible(
        self, branch_id: int, clinic_id: int, current_user: dict
    ) -> bool:
        """Verifica si el usuario autenticado puede ver la sucursal protegida."""
        pass

    @abstractmethod
    async def get_branch_protected_profile(
        self, branch_id: int, clinic_id: int, user_id: int
    ) -> Branch | None:
        """Obtener perfil protegido de una sucursal si el usuario tiene acceso."""
        pass

    @abstractmethod
    async def list_public_branches(
        self,
        clinica_id: int | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Branch], int]:
        """Listar sucursales pblicas segn filtros especificados con paginacin a nivel de base de datos.

        Returns:
            Tuple de (lista de sucursales, total de resultados sin paginar)
        """
        pass


class ServiceRepository(ABC):
    """Interface para el repositorio de servicios."""

    @abstractmethod
    async def get_services_by_branch(self, branch_id: int) -> list[Service]:
        """Obtener servicios por ID de sucursal."""
        pass

    @abstractmethod
    async def list_public_services(
        self,
        sucursal_id: int | None = None,
        clinica_id: int | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Service], int]:
        """Listar servicios pblicos segn filtros especificados con paginacin a nivel de base de datos.

        Returns:
            Tuple de (lista de servicios, total de resultados sin paginar)
        """
        pass


class BranchScheduleRepository(ABC):
    """Interface para el repositorio de horarios."""

    @abstractmethod
    async def get_schedules_by_branch(self, branch_id: int) -> list[BranchSchedule]:
        """Obtener horarios por ID de sucursal."""
        pass


class RatingSummaryRepository(ABC):
    """Interface para el repositorio de resumen de calificaciones."""

    @abstractmethod
    async def get_rating_summary_by_branch(
        self, branch_id: int
    ) -> RatingSummary | None:
        """Obtener resumen de calificaciones por ID de sucursal."""
        pass


class AvailabilitySummaryRepository(ABC):
    """Interface para el repositorio de resumen de disponibilidad."""

    @abstractmethod
    async def get_availability_summary_by_branch(
        self, branch_id: int
    ) -> AvailabilitySummary | None:
        """Obtener resumen de disponibilidad por ID de sucursal."""
        pass
