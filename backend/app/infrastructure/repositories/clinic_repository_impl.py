"""Implementación de repositorios para clínicas y sucursales."""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.domain.repositories.clinic_repository import BranchRepository, ServiceRepository, ScheduleRepository, RatingRepository
from app.domain.entities.clinic import Branch, Service, Schedule, Rating
from app.infrastructure.models.clinic_models import BranchDB, ServiceDB, ScheduleDB, RatingDB


class BranchRepositoryImpl(BranchRepository):
    """Implementación del repositorio de sucursales."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Obtiene una sucursal por ID."""
        db_branch = self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        return Branch.from_orm(db_branch) if db_branch else None

    async def get_branch_by_clinic_and_id(self, clinic_id: int, branch_id: int) -> Optional[Branch]:
        """Obtiene una sucursal por clínica y ID."""
        db_branch = self.db_session.query(BranchDB).filter(
            and_(BranchDB.id == branch_id, BranchDB.clinic_id == clinic_id)
        ).first()
        return Branch.from_orm(db_branch) if db_branch else None

    async def list_active_branches_by_clinic(self, clinic_id: int, skip: int = 0, limit: int = 100) -> List[Branch]:
        """Lista sucursales activas de una clínica con paginación."""
        db_branches = self.db_session.query(BranchDB).filter(
            and_(BranchDB.clinic_id == clinic_id, BranchDB.is_active == True)
        ).offset(skip).limit(limit).all()
        return [Branch.from_orm(branch) for branch in db_branches]

    async def get_branch_schedule(self, branch_id: int) -> List[Schedule]:
        """Obtiene el horario de una sucursal."""
        db_schedules = self.db_session.query(ScheduleDB).filter(
            and_(ScheduleDB.branch_id == branch_id, ScheduleDB.is_closed == False)
        ).order_by(ScheduleDB.day_of_week).all()
        return [Schedule.from_orm(schedule) for schedule in db_schedules]

    async def get_branch_services(self, branch_id: int) -> List[Service]:
        """Obtiene los servicios de una sucursal."""
        db_services = self.db_session.query(ServiceDB).filter(
            and_(ServiceDB.branch_id == branch_id, ServiceDB.is_active == True)
        ).all()
        return [Service.from_orm(service) for service in db_services]

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
        # Para este slice público, cualquier usuario puede acceder
        # En entornos reales podría hacer validaciones de ownership o clínica
        db_branch = self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        return db_branch is not None and db_branch.is_active


class ServiceRepositoryImpl(ServiceRepository):
    """Implementación del repositorio de servicios."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_service_by_branch_and_id(self, branch_id: int, service_id: int) -> Optional[Service]:
        """Obtiene un servicio por sucursal y ID."""
        db_service = self.db_session.query(ServiceDB).filter(
            and_(ServiceDB.id == service_id, ServiceDB.branch_id == branch_id)
        ).first()
        return Service.from_orm(db_service) if db_service else None

    async def list_active_services_by_branch(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """Lista servicios activos de una sucursal con paginación."""
        db_services = self.db_session.query(ServiceDB).filter(
            and_(ServiceDB.branch_id == branch_id, ServiceDB.is_active == True)
        ).offset(skip).limit(limit).all()
        return [Service.from_orm(service) for service in db_services]


class ScheduleRepositoryImpl(ScheduleRepository):
    """Implementación del repositorio de horarios."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def list_schedule_by_branch(self, branch_id: int) -> List[Schedule]:
        """Obtiene el horario de una sucursal."""
        db_schedules = self.db_session.query(ScheduleDB).filter(
            ScheduleDB.branch_id == branch_id
        ).order_by(ScheduleDB.day_of_week).all()
        return [Schedule.from_orm(schedule) for schedule in db_schedules]


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