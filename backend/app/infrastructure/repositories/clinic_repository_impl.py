"""Implementación de repositorios para clínicas y sucursales."""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.domain.repositories.clinic_repository import BranchRepository, ServiceRepository, ScheduleRepository, RatingRepository
from app.domain.entities.clinic import Branch, Service, Schedule, Rating
from app.infrastructure.models.clinic_models import BranchDB, ServiceDB, ScheduleDB, RatingDB
from app.infrastructure.database.models.user import User as UserDB
from app.infrastructure.database.models.owner import Owner as OwnerDB


class BranchRepositoryImpl(BranchRepository):
    """Implementación del repositorio de sucursales."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Obtiene una sucursal por ID."""
        db_branch = self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        if db_branch:
            # For Pydantic v2, we need to use model_validate with from_attributes
            return Branch.model_validate(db_branch, from_attributes=True)
        return None

    async def get_branch_by_clinic_and_id(self, clinic_id: int, branch_id: int) -> Optional[Branch]:
        """Obtiene una sucursal por clínica y ID."""
        db_branch = self.db_session.query(BranchDB).filter(
            and_(BranchDB.id == branch_id, BranchDB.clinic_id == clinic_id)
        ).first()
        if db_branch:
            return Branch.model_validate(db_branch, from_attributes=True)
        return None

    async def list_active_branches_by_clinic(self, clinic_id: int, skip: int = 0, limit: int = 100) -> List[Branch]:
        """Lista sucursales activas de una clínica con paginación."""
        db_branches = self.db_session.query(BranchDB).filter(
            and_(BranchDB.clinic_id == clinic_id, BranchDB.is_active == True)
        ).offset(skip).limit(limit).all()
        return [Branch.model_validate(branch, from_attributes=True) for branch in db_branches]

    async def get_branch_schedule(self, branch_id: int) -> List[Schedule]:
        """Obtiene el horario de una sucursal."""
        # IMPORTANT: Filter to exclude closed schedules as requested
        db_schedules = self.db_session.query(ScheduleDB).filter(
            and_(ScheduleDB.branch_id == branch_id, ScheduleDB.is_closed == False)
        ).order_by(ScheduleDB.day_of_week).all()
        return [Schedule.model_validate(schedule, from_attributes=True) for schedule in db_schedules]

    async def get_branch_services(self, branch_id: int) -> List[Service]:
        """Obtiene los servicios de una sucursal."""
        db_services = self.db_session.query(ServiceDB).filter(
            and_(ServiceDB.branch_id == branch_id, ServiceDB.is_active == True)
        ).all()
        return [Service.model_validate(service, from_attributes=True) for service in db_services]

    async def get_branch_ratings_summary(self, branch_id: int) -> dict:
        """Obtiene un resumen de calificaciones para una sucursal."""
        # Esta implementación es simple: solo retorna el promedio de calificaciones
        # en un entorno real sería más compleja
        
        db_ratings = self.db_session.query(RatingDB).filter(RatingDB.branch_id == branch_id).all()
        
        if not db_ratings:
            return {
                "average_rating": 0.0,
                "total_ratings": 0,
                "rating_distribution": {}
            }
        
        total_rating = sum(rating.rating for rating in db_ratings)
        average = total_rating / len(db_ratings)
        
        # Calcular distribución
        distribution = {}
        for rating in db_ratings:
            stars = rating.rating
            distribution[stars] = distribution.get(stars, 0) + 1
            
        return {
            "average_rating": round(average, 2),
            "total_ratings": len(db_ratings),
            "rating_distribution": distribution
        }

    async def is_branch_accessible(self, branch_id: int, user_id: Optional[int] = None) -> bool:
        """Verifica si el usuario tiene acceso a una sucursal."""
        # Verificar que la sucursal exista y esté activa
        db_branch = self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        if not db_branch or not db_branch.is_active:
            return False

        if user_id is None:
            return False

        db_user = self.db_session.query(UserDB).filter(
            and_(UserDB.id == user_id, UserDB.is_active == True)
        ).first()
        if not db_user:
            return False

        if getattr(db_user, "is_admin", False):
            return True

        db_owner = self.db_session.query(OwnerDB).filter(
            and_(
                OwnerDB.clinic_id == db_branch.clinic_id,
                OwnerDB.email == db_user.email,
                OwnerDB.is_active == True,
            )
        ).first()
        return db_owner is not None


class ServiceRepositoryImpl(ServiceRepository):
    """Implementación del repositorio de servicios."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_service_by_branch_and_id(self, branch_id: int, service_id: int) -> Optional[Service]:
        """Obtiene un servicio por sucursal y ID."""
        db_service = self.db_session.query(ServiceDB).filter(
            and_(ServiceDB.id == service_id, ServiceDB.branch_id == branch_id)
        ).first()
        if db_service:
            return Service.model_validate(db_service, from_attributes=True)
        return None

    async def list_active_services_by_branch(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """Lista servicios activos de una sucursal con paginación."""
        db_services = self.db_session.query(ServiceDB).filter(
            and_(ServiceDB.branch_id == branch_id, ServiceDB.is_active == True)
        ).offset(skip).limit(limit).all()
        return [Service.model_validate(service, from_attributes=True) for service in db_services]


class ScheduleRepositoryImpl(ScheduleRepository):
    """Implementación del repositorio de horarios."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def list_schedule_by_branch(self, branch_id: int) -> List[Schedule]:
        """Obtiene el horario de una sucursal (filtering closed schedules in public profiles)."""
        # IMPORTANT: Filter to exclude closed schedules for public profile access
        db_schedules = self.db_session.query(ScheduleDB).filter(
            and_(ScheduleDB.branch_id == branch_id, ScheduleDB.is_closed == False)
        ).order_by(ScheduleDB.day_of_week).all()
        return [Schedule.model_validate(schedule, from_attributes=True) for schedule in db_schedules]


class RatingRepositoryImpl(RatingRepository):
    """Implementación del repositorio de calificaciones."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_ratings_summary_by_branch(self, branch_id: int) -> dict:
        """Obtiene un resumen de calificaciones para una sucursal."""
        # Esta implementación es simple: solo retorna el promedio de calificaciones
        # en un entorno real sería más compleja
        
        db_ratings = self.db_session.query(RatingDB).filter(RatingDB.branch_id == branch_id).all()
        
        if not db_ratings:
            return {
                "average_rating": 0.0,
                "total_ratings": 0,
                "rating_distribution": {}
            }
        
        total_rating = sum(rating.rating for rating in db_ratings)
        average = total_rating / len(db_ratings)
        
        # Calcular distribución
        distribution = {}
        for rating in db_ratings:
            stars = rating.rating
            distribution[stars] = distribution.get(stars, 0) + 1
            
        return {
            "average_rating": round(average, 2),
            "total_ratings": len(db_ratings),
            "rating_distribution": distribution
        }
