"""Interfaces de repositorios para clínica/sucursal."""
from abc import ABC, abstractmethod
from typing import Optional, List
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
    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Obtener una sucursal por ID."""
        pass
    
    @abstractmethod
    async def get_branch_public_profile(self, branch_id: int) -> Optional[Branch]:
        """Obtener perfil público de una sucursal."""
        pass
    
    @abstractmethod
    async def is_branch_accessible(self, branch_id: int, clinic_id: int, current_user: dict) -> bool:
        """Verifica si el usuario autenticado puede ver la sucursal protegida."""
        pass

    @abstractmethod
    async def get_branch_protected_profile(self, branch_id: int, clinic_id: int, user_id: int) -> Optional[Branch]:
        """Obtener perfil protegido de una sucursal si el usuario tiene acceso."""
        pass


class ServiceRepository(ABC):
    """Interface para el repositorio de servicios."""
    
    @abstractmethod
    async def get_services_by_branch(self, branch_id: int) -> List[Service]:
        """Obtener servicios por ID de sucursal."""
        pass


class BranchScheduleRepository(ABC):
    """Interface para el repositorio de horarios."""
    
    @abstractmethod
    async def get_schedules_by_branch(self, branch_id: int) -> List[BranchSchedule]:
        """Obtener horarios por ID de sucursal."""
        pass


class RatingSummaryRepository(ABC):
    """Interface para el repositorio de resumen de calificaciones."""
    
    @abstractmethod
    async def get_rating_summary_by_branch(self, branch_id: int) -> Optional[RatingSummary]:
        """Obtener resumen de calificaciones por ID de sucursal."""
        pass


class AvailabilitySummaryRepository(ABC):
    """Interface para el repositorio de resumen de disponibilidad."""
    
    @abstractmethod
    async def get_availability_summary_by_branch(self, branch_id: int) -> Optional[AvailabilitySummary]:
        """Obtener resumen de disponibilidad por ID de sucursal."""
        pass
