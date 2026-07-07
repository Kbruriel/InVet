"""SQLAlchemy repositories for clinics, branches, services, schedules, and ratings."""
from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.domain.entities.clinic import Branch, Clinic, Schedule, Service
from app.domain.repositories.clinic_repository import (
    BranchRepository,
    ClinicRepository,
    RatingRepository,
    ScheduleRepository,
    ServiceRepository,
)
from app.infrastructure.database.models.owner import Owner as OwnerDB
from app.infrastructure.database.models.user import User as UserDB
from app.infrastructure.models.clinic_models import (
    BranchDB,
    ClinicDB,
    RatingDB,
    ScheduleDB,
    ServiceDB,
)


def _status_to_active(status: Optional[str]) -> Optional[bool]:
    if status is None:
        return None
    normalized = status.lower()
    if normalized in {"active", "activo", "true", "1"}:
        return True
    if normalized in {"inactive", "inactivo", "false", "0"}:
        return False
    return None


def _clinic_payload(data: dict) -> dict:
    allowed = {
        "name",
        "description",
        "address",
        "city",
        "state",
        "country",
        "postal_code",
        "phone",
        "email",
        "is_active",
    }
    return {key: value for key, value in data.items() if key in allowed}


def _row_data(row) -> dict:
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def _to_clinic(row: ClinicDB) -> Clinic:
    data = _row_data(row)
    data["is_active"] = True if data.get("is_active") is None else data["is_active"]
    data.setdefault("lat", None)
    data.setdefault("lng", None)
    return Clinic.model_validate(data)


def _to_branch(row: BranchDB) -> Branch:
    data = _row_data(row)
    data["is_active"] = True if data.get("is_active") is None else data["is_active"]
    return Branch.model_validate(data)


def _to_service(row: ServiceDB) -> Service:
    data = _row_data(row)
    data["is_active"] = True if data.get("is_active") is None else data["is_active"]
    return Service.model_validate(data)


def _to_schedule(row: ScheduleDB) -> Schedule:
    data = _row_data(row)
    data["is_closed"] = False if data.get("is_closed") is None else data["is_closed"]
    return Schedule.model_validate(data)


class _AccessMixin:
    db_session: Session

    def _get_user(self, user_id: Optional[int]) -> Optional[UserDB]:
        if user_id is None:
            return None
        return (
            self.db_session.query(UserDB)
            .filter(and_(UserDB.id == user_id, UserDB.is_active == True))
            .first()
        )

    def _is_admin(self, user_id: Optional[int]) -> bool:
        user = self._get_user(user_id)
        return bool(user and getattr(user, "is_admin", False))

    def _accessible_clinic_ids(self, user_id: Optional[int]) -> list[int]:
        user = self._get_user(user_id)
        if not user:
            return []
        if getattr(user, "is_admin", False):
            return [
                clinic_id for (clinic_id,) in self.db_session.query(ClinicDB.id).all()
            ]
        return [
            clinic_id
            for (clinic_id,) in self.db_session.query(OwnerDB.clinic_id)
            .filter(
                and_(
                    OwnerDB.email == user.email,
                    OwnerDB.is_active == True,
                    OwnerDB.clinic_id.isnot(None),
                )
            )
            .all()
        ]

    def _user_can_access_clinic(self, clinic_id: int, user_id: Optional[int]) -> bool:
        if user_id is None:
            return False
        if self._is_admin(user_id):
            return (
                self.db_session.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
                is not None
            )
        return clinic_id in self._accessible_clinic_ids(user_id)


class ClinicRepositoryImpl(ClinicRepository, _AccessMixin):
    """SQLAlchemy implementation for clinic administration."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _filtered_query(
        self,
        user_id: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ):
        query = self.db_session.query(ClinicDB)
        if not self._is_admin(user_id):
            clinic_ids = self._accessible_clinic_ids(user_id)
            if not clinic_ids:
                return query.filter(False)
            query = query.filter(ClinicDB.id.in_(clinic_ids))
        active_filter = _status_to_active(status)
        if active_filter is not None:
            query = query.filter(ClinicDB.is_active == active_filter)
        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    ClinicDB.name.ilike(term),
                    ClinicDB.city.ilike(term),
                    ClinicDB.email.ilike(term),
                )
            )
        return query

    async def get_clinic_by_id(self, clinic_id: int) -> Optional[Clinic]:
        db_clinic = (
            self.db_session.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
        )
        return _to_clinic(db_clinic) if db_clinic else None

    async def list_active_clinics(
        self, skip: int = 0, limit: int = 100
    ) -> List[Clinic]:
        db_clinics = (
            self.db_session.query(ClinicDB)
            .filter(ClinicDB.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_to_clinic(clinic) for clinic in db_clinics]

    async def list_clinics(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Clinic]:
        db_clinics = (
            self._filtered_query(user_id, status=status, search=search)
            .order_by(ClinicDB.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_to_clinic(clinic) for clinic in db_clinics]

    async def count_clinics(
        self,
        user_id: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        return self._filtered_query(user_id, status=status, search=search).count()

    async def create_clinic(self, data: dict) -> Clinic:
        db_clinic = ClinicDB(**_clinic_payload(data))
        self.db_session.add(db_clinic)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_clinic)
            return _to_clinic(db_clinic)
        except Exception:
            self.db_session.rollback()
            raise

    async def update_clinic(self, clinic_id: int, data: dict) -> Optional[Clinic]:
        db_clinic = (
            self.db_session.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
        )
        if not db_clinic:
            return None
        for key, value in _clinic_payload(data).items():
            setattr(db_clinic, key, value)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_clinic)
            return _to_clinic(db_clinic)
        except Exception:
            self.db_session.rollback()
            raise

    async def deactivate_clinic(self, clinic_id: int) -> bool:
        db_clinic = (
            self.db_session.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
        )
        if not db_clinic:
            return False
        db_clinic.is_active = False
        try:
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            return False

    async def is_clinic_accessible(
        self, clinic_id: int, user_id: Optional[int]
    ) -> bool:
        return self._user_can_access_clinic(clinic_id, user_id)


class BranchRepositoryImpl(BranchRepository, _AccessMixin):
    """SQLAlchemy implementation for branches."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _filtered_query(
        self,
        user_id: int,
        clinic_id: Optional[int] = None,
        status: Optional[str] = None,
    ):
        query = self.db_session.query(BranchDB)
        if clinic_id is not None:
            query = query.filter(BranchDB.clinic_id == clinic_id)
        elif not self._is_admin(user_id):
            clinic_ids = self._accessible_clinic_ids(user_id)
            if not clinic_ids:
                return query.filter(False)
            query = query.filter(BranchDB.clinic_id.in_(clinic_ids))
        active_filter = _status_to_active(status)
        if active_filter is not None:
            query = query.filter(BranchDB.is_active == active_filter)
        return query

    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        db_branch = (
            self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        )
        return _to_branch(db_branch) if db_branch else None

    async def get_branch_by_clinic_and_id(
        self, clinic_id: int, branch_id: int
    ) -> Optional[Branch]:
        db_branch = (
            self.db_session.query(BranchDB)
            .filter(and_(BranchDB.id == branch_id, BranchDB.clinic_id == clinic_id))
            .first()
        )
        return _to_branch(db_branch) if db_branch else None

    async def list_active_branches_by_clinic(
        self, clinic_id: int, skip: int = 0, limit: int = 100
    ) -> List[Branch]:
        db_branches = (
            self.db_session.query(BranchDB)
            .filter(and_(BranchDB.clinic_id == clinic_id, BranchDB.is_active == True))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_to_branch(branch) for branch in db_branches]

    async def list_branches(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        clinic_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Branch]:
        db_branches = (
            self._filtered_query(user_id=user_id, clinic_id=clinic_id, status=status)
            .order_by(BranchDB.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_to_branch(branch) for branch in db_branches]

    async def count_branches(
        self,
        user_id: int,
        clinic_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        return self._filtered_query(
            user_id=user_id, clinic_id=clinic_id, status=status
        ).count()

    async def create_branch(self, data: dict) -> Branch:
        db_branch = BranchDB(**data)
        self.db_session.add(db_branch)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_branch)
            return _to_branch(db_branch)
        except Exception:
            self.db_session.rollback()
            raise

    async def update_branch(self, branch_id: int, data: dict) -> Optional[Branch]:
        db_branch = (
            self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        )
        if not db_branch:
            return None
        for key, value in data.items():
            setattr(db_branch, key, value)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_branch)
            return _to_branch(db_branch)
        except Exception:
            self.db_session.rollback()
            raise

    async def deactivate_branch(self, branch_id: int) -> bool:
        db_branch = (
            self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        )
        if not db_branch:
            return False
        db_branch.is_active = False
        try:
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            return False

    async def get_branch_schedule(self, branch_id: int) -> List[Schedule]:
        db_schedules = (
            self.db_session.query(ScheduleDB)
            .filter(
                and_(ScheduleDB.branch_id == branch_id, ScheduleDB.is_closed == False)
            )
            .order_by(ScheduleDB.day_of_week)
            .all()
        )
        return [_to_schedule(schedule) for schedule in db_schedules]

    async def get_branch_services(self, branch_id: int) -> List[Service]:
        db_services = (
            self.db_session.query(ServiceDB)
            .filter(and_(ServiceDB.branch_id == branch_id, ServiceDB.is_active == True))
            .all()
        )
        return [_to_service(service) for service in db_services]

    async def get_branch_ratings_summary(self, branch_id: int) -> dict:
        return _ratings_summary(self.db_session, branch_id)

    async def is_branch_accessible(
        self, branch_id: int, user_id: Optional[int] = None
    ) -> bool:
        db_branch = (
            self.db_session.query(BranchDB).filter(BranchDB.id == branch_id).first()
        )
        if not db_branch:
            return False
        return self._user_can_access_clinic(db_branch.clinic_id, user_id)


class ServiceRepositoryImpl(ServiceRepository):
    """SQLAlchemy implementation for services."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_service_by_branch_and_id(
        self, branch_id: int, service_id: int
    ) -> Optional[Service]:
        db_service = (
            self.db_session.query(ServiceDB)
            .filter(and_(ServiceDB.id == service_id, ServiceDB.branch_id == branch_id))
            .first()
        )
        return _to_service(db_service) if db_service else None

    async def list_active_services_by_branch(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Service]:
        db_services = (
            self.db_session.query(ServiceDB)
            .filter(and_(ServiceDB.branch_id == branch_id, ServiceDB.is_active == True))
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_to_service(service) for service in db_services]


class ScheduleRepositoryImpl(ScheduleRepository):
    """SQLAlchemy implementation for schedules."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def list_schedule_by_branch(self, branch_id: int) -> List[Schedule]:
        db_schedules = (
            self.db_session.query(ScheduleDB)
            .filter(
                and_(ScheduleDB.branch_id == branch_id, ScheduleDB.is_closed == False)
            )
            .order_by(ScheduleDB.day_of_week)
            .all()
        )
        return [_to_schedule(schedule) for schedule in db_schedules]

    async def list_branch_hours(self, branch_id: int) -> List[Schedule]:
        db_schedules = (
            self.db_session.query(ScheduleDB)
            .filter(ScheduleDB.branch_id == branch_id)
            .order_by(ScheduleDB.day_of_week)
            .all()
        )
        return [_to_schedule(schedule) for schedule in db_schedules]

    async def get_schedule_by_id(
        self, branch_id: int, schedule_id: int
    ) -> Optional[Schedule]:
        db_schedule = (
            self.db_session.query(ScheduleDB)
            .filter(
                and_(ScheduleDB.id == schedule_id, ScheduleDB.branch_id == branch_id)
            )
            .first()
        )
        return _to_schedule(db_schedule) if db_schedule else None

    async def create_schedule(self, branch_id: int, data: dict) -> Schedule:
        db_schedule = ScheduleDB(branch_id=branch_id, **data)
        self.db_session.add(db_schedule)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_schedule)
            return _to_schedule(db_schedule)
        except Exception:
            self.db_session.rollback()
            raise

    async def update_schedule(
        self, branch_id: int, schedule_id: int, data: dict
    ) -> Optional[Schedule]:
        db_schedule = (
            self.db_session.query(ScheduleDB)
            .filter(
                and_(ScheduleDB.id == schedule_id, ScheduleDB.branch_id == branch_id)
            )
            .first()
        )
        if not db_schedule:
            return None
        for key, value in data.items():
            setattr(db_schedule, key, value)
        try:
            self.db_session.commit()
            self.db_session.refresh(db_schedule)
            return _to_schedule(db_schedule)
        except Exception:
            self.db_session.rollback()
            raise

    async def delete_schedule(self, branch_id: int, schedule_id: int) -> bool:
        db_schedule = (
            self.db_session.query(ScheduleDB)
            .filter(
                and_(ScheduleDB.id == schedule_id, ScheduleDB.branch_id == branch_id)
            )
            .first()
        )
        if not db_schedule:
            return False
        self.db_session.delete(db_schedule)
        try:
            self.db_session.commit()
            return True
        except Exception:
            self.db_session.rollback()
            return False


class RatingRepositoryImpl(RatingRepository):
    """SQLAlchemy implementation for ratings."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_ratings_summary_by_branch(self, branch_id: int) -> dict:
        return _ratings_summary(self.db_session, branch_id)


def _ratings_summary(db_session: Session, branch_id: int) -> dict:
    db_ratings = (
        db_session.query(RatingDB).filter(RatingDB.branch_id == branch_id).all()
    )
    if not db_ratings:
        return {"average_rating": 0.0, "total_ratings": 0, "rating_distribution": {}}

    average = sum(rating.rating for rating in db_ratings) / len(db_ratings)
    distribution = {}
    for rating in db_ratings:
        distribution[rating.rating] = distribution.get(rating.rating, 0) + 1

    return {
        "average_rating": round(average, 2),
        "total_ratings": len(db_ratings),
        "rating_distribution": distribution,
    }
