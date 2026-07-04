"""Casos de uso para clínicas y sucursales."""
from typing import Optional, List, Dict
from app.domain.entities.clinic import Clinic, Branch, Service, Schedule, Rating
from app.domain.repositories.clinic_repository import BranchRepository, ServiceRepository, ScheduleRepository, RatingRepository


class GetBranchProfileUseCase:
    """Caso de uso para obtener el perfil público de una sucursal."""
    
    def __init__(
        self,
        branch_repo: BranchRepository,
        service_repo: ServiceRepository,
        schedule_repo: ScheduleRepository,
        rating_repo: RatingRepository
    ):
        self.branch_repo = branch_repo
        self.service_repo = service_repo
        self.schedule_repo = schedule_repo
        self.rating_repo = rating_repo

    async def execute(self, branch_id: int) -> Dict:
        """Ejecuta el caso de uso para obtener el perfil público de una sucursal."""
        
        # Verificar que la sucursal exista y sea accesible
        branch = await self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            # En un entorno real, se debería usar una excepción personalizada
            # pero por ahora vamos a mantener el manejo consistente con el API
            raise ValueError(f"Branch with id {branch_id} not found")
        
        # Validar si el usuario tiene acceso (si aplica en contextos auth)
        # En este caso, es público por lo que no hay validación de ownership
        
        # Obtener información de la sucursal
        branch_data = branch.dict()
        
        # Obtener servicios
        services = await self.service_repo.list_active_services_by_branch(branch_id)
        services_data = [service.dict() for service in services]
        
        # Obtener horarios
        schedules = await self.schedule_repo.list_schedule_by_branch(branch_id)
        schedules_data = [schedule.dict() for schedule in schedules]
        
        # Obtener resumen de calificaciones
        ratings_summary = await self.rating_repo.get_ratings_summary_by_branch(branch_id)
        
        # Combinar toda la información en una respuesta pública
        result = {
            "branch": branch_data,
            "services": services_data,
            "schedules": schedules_data,
            "ratings_summary": ratings_summary
        }
        
        return result


class GetBranchProfileWithPermissionUseCase:
    """Caso de uso para obtener el perfil público de una sucursal con validación de permisos."""
    
    def __init__(
        self,
        branch_repo: BranchRepository,
        service_repo: ServiceRepository,
        schedule_repo: ScheduleRepository,
        rating_repo: RatingRepository
    ):
        self.branch_repo = branch_repo
        self.service_repo = service_repo
        self.schedule_repo = schedule_repo
        self.rating_repo = rating_repo

    async def execute(self, clinic_id: int, branch_id: int, user_id: Optional[int] = None) -> Dict:
        """Ejecuta el caso de uso para obtener el perfil público de una sucursal."""
        
        # Verificar acceso a la sucursal antes de continuar
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            # Para mantener consistencia con el manejo actual en API,
            # lanzamos un ValueError que será convertido a HTTP 403 por el controlador
            raise ValueError("Access denied to branch")
            
        # Obtener información de la sucursal
        branch = await self.branch_repo.get_branch_by_clinic_and_id(clinic_id, branch_id)
        if not branch:
            raise ValueError(f"Branch with id {branch_id} not found in clinic {clinic_id}")
        
        # Obtener información de la sucursal
        branch_data = branch.dict()
        
        # Obtener servicios
        services = await self.service_repo.list_active_services_by_branch(branch_id)
        services_data = [service.dict() for service in services]
        
        # Obtener horarios
        schedules = await self.schedule_repo.list_schedule_by_branch(branch_id)
        schedules_data = [schedule.dict() for schedule in schedules]
        
        # Obtener resumen de calificaciones
        ratings_summary = await self.rating_repo.get_ratings_summary_by_branch(branch_id)
        
        # Combinar toda la información en una respuesta pública
        result = {
            "branch": branch_data,
            "services": services_data,
            "schedules": schedules_data,
            "ratings_summary": ratings_summary
        }
        
        return result


# Use case para lista de sucursales públicas (no se implementa en MVP por ahora)
class ListBranchesUseCase:
    """Caso de uso para listar sucursales."""
    
    def __init__(self, branch_repo: BranchRepository):
        self.branch_repo = branch_repo

    async def execute(self, clinic_id: int, skip: int = 0, limit: int = 100) -> List[Branch]:
        """Ejecuta el caso de uso para listar sucursales."""
        return await self.branch_repo.list_active_branches_by_clinic(clinic_id, skip, limit)