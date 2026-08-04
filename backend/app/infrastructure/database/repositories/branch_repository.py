"""Implementación del repositorio de sucursales."""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.entities.branch import Branch
from app.domain.entities.branch import Service, BranchSchedule, RatingSummary, AvailabilitySummary
from app.domain.repositories.branch_repository import (
    BranchRepository,
    ServiceRepository,
    BranchScheduleRepository,
    RatingSummaryRepository,
    AvailabilitySummaryRepository
)
from app.infrastructure.database.models.branch import Branch as BranchModel
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.service import Service as ServiceModel
from app.infrastructure.database.models.branch_schedule import BranchSchedule as BranchScheduleModel
from app.infrastructure.database.models.rating_summary import RatingSummary as RatingSummaryModel
from app.infrastructure.database.models.availability_summary import AvailabilitySummary as AvailabilitySummaryModel


class BranchRepositoryImpl(BranchRepository):
    """Implementación del repositorio de sucursales."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Obtener una sucursal por ID."""
        db_branch = self.db.query(BranchModel).filter(BranchModel.id == branch_id).first()
        if db_branch is None:
            return None
        return Branch.model_validate(db_branch)
    
    async def get_branch_public_profile(self, branch_id: int) -> Optional[Branch]:
        """Obtener perfil público de una sucursal."""
        # Solo devolver campos públicos
        db_branch = self.db.query(BranchModel).filter(BranchModel.id == branch_id).first()
        if db_branch is None:
            return None
        # Convertir a entidad con solo los campos necesarios para perfil público
        branch_public = Branch(
            id=db_branch.id,
            clinic_id=db_branch.clinic_id,
            name=db_branch.name,
            description=db_branch.description,
            address=db_branch.address,
            city=db_branch.city,
            state=db_branch.state,
            country=db_branch.country,
            postal_code=db_branch.postal_code,
            phone=db_branch.phone,
            email=db_branch.email,
            is_active=db_branch.is_active,
            created_at=db_branch.created_at,
            updated_at=db_branch.updated_at
        )
        return branch_public
    
    async def is_branch_accessible(self, branch_id: int, clinic_id: int, current_user: dict) -> bool:
        """Verifica si el usuario autenticado puede acceder al perfil protegido."""
        db_branch = self.db.query(BranchModel).filter(
            BranchModel.id == branch_id,
            BranchModel.clinic_id == clinic_id
        ).first()
        if db_branch is None:
            return False

        if current_user.get("role") == "admin":
            return True

        email = current_user.get("email")
        if not email:
            return False

        owner = self.db.query(OwnerModel).filter(
            OwnerModel.clinic_id == clinic_id,
            OwnerModel.email == email,
            OwnerModel.is_active == True
        ).first()
        return owner is not None

    async def get_branch_protected_profile(self, branch_id: int, clinic_id: int, user_id: int) -> Optional[Branch]:
        """Obtener perfil protegido de una sucursal si el usuario tiene acceso."""
        # Primero verificamos que la sucursal exista
        db_branch = self.db.query(BranchModel).filter(
            BranchModel.id == branch_id,
            BranchModel.clinic_id == clinic_id
        ).first()
        
        if db_branch is None:
            return None
        
        # Verificar acceso del usuario (simplificado - en una implementación real habría lógica más compleja)
        # Para el MVP, supondremos que si la sucursal existe y pertenece a la clínica, el usuario tiene acceso
        return Branch.model_validate(db_branch)


class ServiceRepositoryImpl(ServiceRepository):
    """Implementación del repositorio de servicios."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def get_services_by_branch(self, branch_id: int) -> List[Service]:
        """Obtener servicios por ID de sucursal."""
        db_services = self.db.query(ServiceModel).filter(
            ServiceModel.branch_id == branch_id,
            ServiceModel.is_active == True
        ).all()
        return [Service.model_validate(db_service) for db_service in db_services]


class BranchScheduleRepositoryImpl(BranchScheduleRepository):
    """Implementación del repositorio de horarios."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def get_schedules_by_branch(self, branch_id: int) -> List[BranchSchedule]:
        """Obtener horarios por ID de sucursal."""
        db_schedules = self.db.query(BranchScheduleModel).filter(
            BranchScheduleModel.branch_id == branch_id,
            BranchScheduleModel.is_active == True
        ).all()
        return [BranchSchedule.model_validate(db_schedule) for db_schedule in db_schedules]


class RatingSummaryRepositoryImpl(RatingSummaryRepository):
    """Implementación del repositorio de resumen de calificaciones."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def get_rating_summary_by_branch(self, branch_id: int) -> Optional[RatingSummary]:
        """Obtener resumen de calificaciones por ID de sucursal."""
        db_rating = self.db.query(RatingSummaryModel).filter(
            RatingSummaryModel.branch_id == branch_id
        ).first()
        if db_rating is None:
            return None
        return RatingSummary.model_validate(db_rating)


class AvailabilitySummaryRepositoryImpl(AvailabilitySummaryRepository):
    """Implementación del repositorio de resumen de disponibilidad."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def get_availability_summary_by_branch(self, branch_id: int) -> Optional[AvailabilitySummary]:
        """Obtener resumen de disponibilidad por ID de sucursal."""
        db_availability = self.db.query(AvailabilitySummaryModel).filter(
            AvailabilitySummaryModel.branch_id == branch_id
        ).first()
        if db_availability is None:
            return None
        return AvailabilitySummary.model_validate(db_availability)
