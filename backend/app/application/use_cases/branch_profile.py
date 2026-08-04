"""Casos de uso para perfiles de clínica/sucursal."""
from typing import Optional

from app.domain.entities.branch import Branch, RatingSummary, AvailabilitySummary
from app.domain.repositories.branch_repository import (
    BranchRepository,
    ServiceRepository,
    BranchScheduleRepository,
    RatingSummaryRepository,
    AvailabilitySummaryRepository
)


class GetBranchPublicProfileUseCase:
    """Caso de uso para obtener perfil público de sucursal."""
    
    def __init__(
        self,
        branch_repo: BranchRepository,
        service_repo: ServiceRepository,
        schedule_repo: BranchScheduleRepository,
        rating_repo: RatingSummaryRepository,
        availability_repo: AvailabilitySummaryRepository
    ):
        self.branch_repo = branch_repo
        self.service_repo = service_repo
        self.schedule_repo = schedule_repo
        self.rating_repo = rating_repo
        self.availability_repo = availability_repo
    
    async def execute(self, branch_id: int) -> Optional[Branch]:
        """Ejecutar el caso de uso para obtener perfil público.

        Nota: El endpoint público devuelve campos públicos (no expone
        datos administrativos). Si branch es None la responsabilidad de
        retornar 404 corresponde al router.
        """
        # Obtener la sucursal básica
        branch = await self.branch_repo.get_branch_public_profile(branch_id)
        if not branch:
            return None
        
        # Cargar servicios asociados (lista vacía es válida — M1 mitigation)
        services = await self.service_repo.get_services_by_branch(branch_id)
        branch.services = services if services else []
        
        # Cargar horarios asociados
        schedules = await self.schedule_repo.get_schedules_by_branch(branch_id)
        branch.schedules = schedules if schedules else []
        
        # Cargar resumen de calificaciones
        rating_summary = await self.rating_repo.get_rating_summary_by_branch(branch_id)
        if rating_summary:
            branch.rating_summary = rating_summary
        else:
            # Si no hay ratings aún, devolver objeto vacío en lugar de None
            branch.rating_summary = RatingSummary(
                id=0,
                branch_id=branch_id,
                average_rating=0.0,
                total_reviews=0,
                review_distribution="{}",
                created_at=None,
                updated_at=None,
            )
        
        # Cargar resumen de disponibilidad (puede ser None si no hay datos)
        availability_summary = await self.availability_repo.get_availability_summary_by_branch(branch_id)
        if availability_summary:
            branch.availability_summary = availability_summary
        else:
            branch.availability_summary = AvailabilitySummary(
                id=0,
                branch_id=branch_id,
                is_available=False,
                next_available_time=None,
                availability_type="unknown",
                created_at=None,
                updated_at=None,
            )
        
        return branch


class GetBranchProtectedProfileUseCase:
    """Caso de uso para obtener perfil protegido de sucursal."""
    
    def __init__(
        self,
        branch_repo: BranchRepository,
        service_repo: ServiceRepository,
        schedule_repo: BranchScheduleRepository,
        rating_repo: RatingSummaryRepository,
        availability_repo: AvailabilitySummaryRepository
    ):
        self.branch_repo = branch_repo
        self.service_repo = service_repo
        self.schedule_repo = schedule_repo
        self.rating_repo = rating_repo
        self.availability_repo = availability_repo
    
    async def execute(self, branch_id: int, clinic_id: int, current_user: dict) -> Optional[Branch]:
        """Ejecutar el caso de uso para obtener perfil protegido.

        Valida ownership antes de devolver datos. Si la sucursal no
        pertenece a clinic o el usuario no tiene acceso, se devuelve None
        en lugar de los datos (responsabilidad del router retornar 403/404).
        """
        # Validación de ownership explícita antes de cargar datos
        if not await self.branch_repo.is_branch_accessible(branch_id, clinic_id, current_user):
            return None

        branch = await self.branch_repo.get_branch_protected_profile(
            branch_id,
            clinic_id,
            current_user.get("id", 0),
        )
        if not branch or branch.clinic_id != clinic_id:
            return None
        
        # Cargar servicios asociados
        services = await self.service_repo.get_services_by_branch(branch_id)
        branch.services = services if services else []
        
        # Cargar horarios asociados
        schedules = await self.schedule_repo.get_schedules_by_branch(branch_id)
        branch.schedules = schedules if schedules else []
        
        # Cargar resumen de calificaciones
        rating_summary = await self.rating_repo.get_rating_summary_by_branch(branch_id)
        if rating_summary:
            branch.rating_summary = rating_summary
        
        # Cargar resumen de disponibilidad
        availability_summary = await self.availability_repo.get_availability_summary_by_branch(branch_id)
        if availability_summary:
            branch.availability_summary = availability_summary
        
        return branch
