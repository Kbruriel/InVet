"""Implementacion del repositorio de sucursales."""

from sqlalchemy.orm import Session

from app.domain.entities.branch import (
    AvailabilitySummary,
    Branch,
    BranchSchedule,
    RatingSummary,
    Service,
)
from app.domain.repositories.branch_repository import (
    AvailabilitySummaryRepository,
    BranchRepository,
    BranchScheduleRepository,
    RatingSummaryRepository,
    ServiceRepository,
)
from app.infrastructure.database.models.availability_summary import (
    AvailabilitySummary as AvailabilitySummaryModel,
)
from app.infrastructure.database.models.branch import Branch as BranchModel
from app.infrastructure.database.models.branch_schedule import (
    BranchSchedule as BranchScheduleModel,
)
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.rating_summary import (
    RatingSummary as RatingSummaryModel,
)
from app.infrastructure.database.models.service_model import Service as ServiceModel


class BranchRepositoryImpl(BranchRepository):
    """Implementacion del repositorio de sucursales."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_branch_by_id(self, branch_id: int) -> Branch | None:
        """Obtener una sucursal por ID."""
        db_branch = (
            self.db.query(BranchModel).filter(BranchModel.id == branch_id).first()
        )
        if db_branch is None:
            return None
        return Branch.model_validate(db_branch)

    async def get_branch_public_profile(self, branch_id: int) -> Branch | None:
        """Obtener perfil publico de una sucursal."""
        db_branch = (
            self.db.query(BranchModel).filter(BranchModel.id == branch_id).first()
        )
        if db_branch is None:
            return None
        return Branch.model_validate(db_branch)

    async def is_branch_accessible(
        self, branch_id: int, clinic_id: int, current_user: dict
    ) -> bool:
        """Verifica si el usuario autenticado puede acceder al perfil protegido."""
        db_branch = (
            self.db.query(BranchModel)
            .filter(BranchModel.id == branch_id, BranchModel.clinic_id == clinic_id)
            .first()
        )
        if db_branch is None:
            return False

        if current_user.get("role") == "admin":
            return True

        email = current_user.get("email")
        if not email:
            return False

        owner = (
            self.db.query(OwnerModel)
            .filter(
                OwnerModel.clinic_id == clinic_id,
                OwnerModel.email == email,
                OwnerModel.is_active.is_(True),
            )
            .first()
        )
        return owner is not None

    async def get_branch_protected_profile(
        self, branch_id: int, clinic_id: int, user_id: int
    ) -> Branch | None:
        """Obtener perfil protegido de una sucursal si el usuario tiene acceso."""
        db_branch = (
            self.db.query(BranchModel)
            .filter(BranchModel.id == branch_id, BranchModel.clinic_id == clinic_id)
            .first()
        )
        if db_branch is None:
            return None
        return Branch.model_validate(db_branch)

    async def list_public_branches(
        self,
        clinica_id: int | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Branch], int]:
        """Listar sucursales pblicas segn filtros especificados con paginacin a nivel de base de datos."""
        query = self.db.query(BranchModel).filter(BranchModel.is_active.is_(True))

        # Filtrar por clnica si se proporciona
        if clinica_id:
            query = query.filter(BranchModel.clinic_id == clinica_id)

        # Filtrar por nombre o ciudad si se proporciona
        if search:
            search_lower = search.lower()
            query = query.filter(
                (BranchModel.name.ilike(f"%{search_lower}%"))
                | (BranchModel.city.ilike(f"%{search_lower}%"))
            )

        # Obtener conteo total antes de paginar
        total = query.count()

        # Aplicar paginacin a nivel de SQL
        offset = (page - 1) * size
        db_branches = query.offset(offset).limit(size).all()
        return [Branch.model_validate(db_branch) for db_branch in db_branches], total


class ServiceRepositoryImpl(ServiceRepository):
    """Implementacion del repositorio de servicios."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_services_by_branch(self, branch_id: int) -> list[Service]:
        """Obtener servicios por ID de sucursal."""
        db_services = (
            self.db.query(ServiceModel)
            .filter(
                ServiceModel.branch_id == branch_id, ServiceModel.is_active.is_(True)
            )
            .all()
        )
        return [Service.model_validate(db_service) for db_service in db_services]

    async def list_public_services(
        self,
        sucursal_id: int | None = None,
        clinica_id: int | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Service], int]:
        """Listar servicios pblicos segn filtros especificados con paginacin a nivel de base de datos.

        Si se proporciona clinica_id sin sucursal_id, se filtran servicios de todas las sucursales de esa clnica.
        """
        query = self.db.query(ServiceModel).filter(
            ServiceModel.is_active.is_(True)
        )

        # Filtrar por sucursal si se proporciona
        if sucursal_id:
            query = query.filter(ServiceModel.branch_id == sucursal_id)
        elif clinica_id:
            # Filtrar por todas las sucursales de la clnica
            subquery = self.db.query(BranchModel.id).filter(
                BranchModel.clinic_id == clinica_id,
                BranchModel.is_active.is_(True)
            )
            query = query.filter(ServiceModel.branch_id.in_(subquery))

        # Filtrar por nombre si se proporciona
        if search:
            search_lower = search.lower()
            query = query.filter(ServiceModel.name.ilike(f"%{search_lower}%"))

        # Obtener conteo total antes de paginar
        total = query.count()

        # Aplicar paginacin a nivel de SQL
        offset = (page - 1) * size
        db_services = query.offset(offset).limit(size).all()
        return [Service.model_validate(db_service) for db_service in db_services], total


class BranchScheduleRepositoryImpl(BranchScheduleRepository):
    """Implementacion del repositorio de horarios."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_schedules_by_branch(self, branch_id: int) -> list[BranchSchedule]:
        """Obtener horarios por ID de sucursal."""
        db_schedules = (
            self.db.query(BranchScheduleModel)
            .filter(
                BranchScheduleModel.branch_id == branch_id,
                BranchScheduleModel.is_active.is_(True),
            )
            .all()
        )
        return [
            BranchSchedule.model_validate(db_schedule) for db_schedule in db_schedules
        ]


class RatingSummaryRepositoryImpl(RatingSummaryRepository):
    """Implementacion del repositorio de resumen de calificaciones."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_rating_summary_by_branch(
        self, branch_id: int
    ) -> RatingSummary | None:
        """Obtener resumen de calificaciones por ID de sucursal."""
        db_rating = (
            self.db.query(RatingSummaryModel)
            .filter(RatingSummaryModel.branch_id == branch_id)
            .first()
        )
        if db_rating is None:
            return None
        return RatingSummary.model_validate(db_rating)


class AvailabilitySummaryRepositoryImpl(AvailabilitySummaryRepository):
    """Implementacion del repositorio de resumen de disponibilidad."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def get_availability_summary_by_branch(
        self, branch_id: int
    ) -> AvailabilitySummary | None:
        """Obtener resumen de disponibilidad por ID de sucursal."""
        db_availability = (
            self.db.query(AvailabilitySummaryModel)
            .filter(AvailabilitySummaryModel.branch_id == branch_id)
            .first()
        )
        if db_availability is None:
            return None
        return AvailabilitySummary.model_validate(db_availability)
