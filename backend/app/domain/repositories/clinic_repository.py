"""Interfaz del repositorio de clínicas y sucursales."""
from typing import Optional, List
from abc import ABC, abstractmethod
from app.domain.entities.clinic import Clinic, Branch, Service, Schedule, Rating


class ClinicRepository(ABC):
    """Interfaz para el repositorio de clínicas."""
    
    @abstractmethod
    async def get_clinic_by_id(self, clinic_id: int) -> Optional[Clinic]:
        """Obtiene una clínica por ID."""
        pass
    
    @abstractmethod
    async def list_active_clinics(self, skip: int = 0, limit: int = 100) -> List[Clinic]:
        """Lista clínicas activas con paginación."""
        pass


class BranchRepository(ABC):
    """Interfaz para el repositorio de sucursales."""
    
    @abstractmethod
    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Obtiene una sucursal por ID."""
        pass
    
    @abstractmethod
    async def get_branch_by_clinic_and_id(self, clinic_id: int, branch_id: int) -> Optional[Branch]:
        """Obtiene una sucursal por clínica y ID."""
        pass
    
    @abstractmethod
    async def list_active_branches_by_clinic(self, clinic_id: int, skip: int = 0, limit: int = 100) -> List[Branch]:
        """Lista sucursales activas de una clínica con paginación."""
        pass

    @abstractmethod
    async def get_branch_schedule(self, branch_id: int) -> List[Schedule]:
        """Obtiene el horario de una sucursal."""
        pass

    @abstractmethod
    async def get_branch_services(self, branch_id: int) -> List[Service]:
        """Obtiene los servicios de una sucursal."""
        pass

    @abstractmethod
    async def get_branch_ratings_summary(self, branch_id: int) -> dict:
        """Obtiene un resumen de calificaciones para una sucursal."""
        pass

    @abstractmethod
    async def is_branch_accessible(self, branch_id: int, user_id: Optional[int] = None) -> bool:
        """Verifica si el usuario tiene acceso a una sucursal."""
        pass


class ServiceRepository(ABC):
    """Interfaz para el repositorio de servicios."""
    
    @abstractmethod
    async def get_service_by_branch_and_id(self, branch_id: int, service_id: int) -> Optional[Service]:
        """Obtiene un servicio por sucursal y ID."""
        pass
    
    @abstractmethod
    async def list_active_services_by_branch(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """Lista servicios activos de una sucursal con paginación."""
        pass


class ScheduleRepository(ABC):
    """Interfaz para el repositorio de horarios."""
    
    @abstractmethod
    async def list_schedule_by_branch(self, branch_id: int) -> List[Schedule]:
        """Obtiene el horario de una sucursal."""
        pass


class RatingRepository(ABC):
    """Interfaz para el repositorio de calificaciones."""
    
    @abstractmethod
    async def get_ratings_summary_by_branch(self, branch_id: int) -> dict:
        """Obtiene un resumen de calificaciones para una sucursal."""
        pass