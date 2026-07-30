"""Use cases for clinics, branches, and branch hours."""

from typing import Dict, List, Optional

from app.domain.entities.clinic import Branch, Clinic, Schedule
from app.domain.repositories.clinic_repository import (
    BranchRepository,
    ClinicRepository,
    RatingRepository,
    ScheduleRepository,
    ServiceRepository,
)


def _clean_payload(data: dict) -> dict:
    """Drop unset values before passing payloads to repositories.

    Rationale: Pydantic schemas with ``exclude_unset=True`` produce a dict that
    still contains keys whose resolved value is ``None`` (e.g. the literal ``null``
    in JSON).  These nulls cause SQLAlchemy / repository upsert logic to overwrite
    existing columns with empty values instead of treating them as "field not
    supplied".  Filtering out ``None`` values ensures a true *partial-update*
    semantics: only explicitly populated fields are sent down to the DB layer.

    This helper is intentionally kept in the use-case layer because the rule is
    business-policy (which fields count as "unset") and it shields the
    infrastructure layer from HTTP-layer serialization artefacts.
    """
    return {key: value for key, value in data.items() if value is not None}


def _ensure_authenticated(user_id: Optional[int]) -> int:
    if user_id is None:
        raise ValueError("Access denied")
    return user_id


def _validate_schedule_payload(data: dict) -> None:
    is_closed = data.get("is_closed", False)
    if not is_closed and (not data.get("open_time") or not data.get("close_time")):
        raise ValueError("Invalid schedule hours")


class GetBranchProfileUseCase:
    """Use case for the public branch profile."""

    def __init__(
        self,
        branch_repo: BranchRepository,
        service_repo: ServiceRepository,
        schedule_repo: ScheduleRepository,
        rating_repo: RatingRepository,
    ):
        self.branch_repo = branch_repo
        self.service_repo = service_repo
        self.schedule_repo = schedule_repo
        self.rating_repo = rating_repo

    async def execute(self, branch_id: int) -> Dict:
        """Return public data for a branch."""
        branch = await self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            raise ValueError(f"Branch with id {branch_id} not found")

        services = await self.service_repo.list_active_services_by_branch(branch_id)
        schedules = await self.schedule_repo.list_schedule_by_branch(branch_id)
        ratings_summary = await self.rating_repo.get_ratings_summary_by_branch(
            branch_id
        )

        return {
            "branch": branch.model_dump(),
            "services": [service.model_dump() for service in services],
            "schedules": [schedule.model_dump() for schedule in schedules],
            "ratings_summary": ratings_summary,
        }


class GetBranchProfileWithPermissionUseCase:
    """Use case for the protected branch profile."""

    def __init__(
        self,
        branch_repo: BranchRepository,
        service_repo: ServiceRepository,
        schedule_repo: ScheduleRepository,
        rating_repo: RatingRepository,
    ):
        self.branch_repo = branch_repo
        self.service_repo = service_repo
        self.schedule_repo = schedule_repo
        self.rating_repo = rating_repo

    async def execute(
        self, clinic_id: int, branch_id: int, user_id: Optional[int] = None
    ) -> Dict:
        """Return branch data after validating access."""
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")

        branch = await self.branch_repo.get_branch_by_clinic_and_id(
            clinic_id, branch_id
        )
        if not branch:
            raise ValueError(
                f"Branch with id {branch_id} not found in clinic {clinic_id}"
            )

        services = await self.service_repo.list_active_services_by_branch(branch_id)
        schedules = await self.schedule_repo.list_schedule_by_branch(branch_id)
        ratings_summary = await self.rating_repo.get_ratings_summary_by_branch(
            branch_id
        )

        return {
            "branch": branch.model_dump(),
            "services": [service.model_dump() for service in services],
            "schedules": [schedule.model_dump() for schedule in schedules],
            "ratings_summary": ratings_summary,
        }


class ListBranchesUseCase:
    """Use case for listing active branches by clinic."""

    def __init__(self, branch_repo: BranchRepository):
        self.branch_repo = branch_repo

    async def execute(
        self, clinic_id: int, skip: int = 0, limit: int = 100
    ) -> List[Branch]:
        """Return active branches for a clinic."""
        return await self.branch_repo.list_active_branches_by_clinic(
            clinic_id, skip, limit
        )


class ClinicAdminUseCase:
    """Administration use cases for clinics."""

    def __init__(self, clinic_repo: ClinicRepository):
        self.clinic_repo = clinic_repo

    async def list_clinics(
        self,
        user_id: Optional[int],
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> dict:
        user_id = _ensure_authenticated(user_id)
        items = await self.clinic_repo.list_clinics(
            user_id=user_id, skip=skip, limit=limit, status=status, search=search
        )
        total = await self.clinic_repo.count_clinics(
            user_id=user_id, status=status, search=search
        )
        return {
            "items": items,
            "pagination": {"skip": skip, "limit": limit, "total": total},
        }

    async def get_clinic(self, clinic_id: int, user_id: Optional[int]) -> Clinic:
        user_id = _ensure_authenticated(user_id)
        if not await self.clinic_repo.is_clinic_accessible(clinic_id, user_id):
            raise ValueError("Access denied to clinic")
        clinic = await self.clinic_repo.get_clinic_by_id(clinic_id)
        if not clinic:
            raise ValueError(f"Clinic with id {clinic_id} not found")
        return clinic

    async def create_clinic(self, data: dict, user_id: Optional[int]) -> Clinic:
        _ensure_authenticated(user_id)
        return await self.clinic_repo.create_clinic(_clean_payload(data))

    async def update_clinic(
        self, clinic_id: int, data: dict, user_id: Optional[int]
    ) -> Clinic:
        user_id = _ensure_authenticated(user_id)
        if not await self.clinic_repo.is_clinic_accessible(clinic_id, user_id):
            raise ValueError("Access denied to clinic")
        clinic = await self.clinic_repo.update_clinic(clinic_id, _clean_payload(data))
        if not clinic:
            raise ValueError(f"Clinic with id {clinic_id} not found")
        return clinic

    async def deactivate_clinic(self, clinic_id: int, user_id: Optional[int]) -> None:
        user_id = _ensure_authenticated(user_id)
        if not await self.clinic_repo.is_clinic_accessible(clinic_id, user_id):
            raise ValueError("Access denied to clinic")
        if not await self.clinic_repo.deactivate_clinic(clinic_id):
            raise ValueError(f"Clinic with id {clinic_id} not found")


class BranchAdminUseCase:
    """Administration use cases for branches."""

    def __init__(
        self,
        branch_repo: BranchRepository,
        clinic_repo: ClinicRepository,
    ):
        self.branch_repo = branch_repo
        self.clinic_repo = clinic_repo

    async def list_branches(
        self,
        user_id: Optional[int],
        skip: int = 0,
        limit: int = 100,
        clinic_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> dict:
        user_id = _ensure_authenticated(user_id)
        if clinic_id is not None and not await self.clinic_repo.is_clinic_accessible(
            clinic_id, user_id
        ):
            raise ValueError("Access denied to clinic")
        items = await self.branch_repo.list_branches(
            user_id=user_id,
            skip=skip,
            limit=limit,
            clinic_id=clinic_id,
            status=status,
        )
        total = await self.branch_repo.count_branches(
            user_id=user_id, clinic_id=clinic_id, status=status
        )
        return {
            "items": items,
            "pagination": {"skip": skip, "limit": limit, "total": total},
        }

    async def get_branch(self, branch_id: int, user_id: Optional[int]) -> Branch:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        branch = await self.branch_repo.get_branch_by_id(branch_id)
        if not branch:
            raise ValueError(f"Branch with id {branch_id} not found")
        return branch

    async def create_branch(self, data: dict, user_id: Optional[int]) -> Branch:
        user_id = _ensure_authenticated(user_id)
        payload = _clean_payload(data)
        clinic_id = payload.get("clinic_id")
        if not isinstance(clinic_id, int):
            raise ValueError("clinic_id is required")
        if not await self.clinic_repo.is_clinic_accessible(clinic_id, user_id):
            raise ValueError("Access denied to clinic")
        return await self.branch_repo.create_branch(payload)

    async def update_branch(
        self, branch_id: int, data: dict, user_id: Optional[int]
    ) -> Branch:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        branch = await self.branch_repo.update_branch(branch_id, _clean_payload(data))
        if not branch:
            raise ValueError(f"Branch with id {branch_id} not found")
        return branch

    async def deactivate_branch(self, branch_id: int, user_id: Optional[int]) -> None:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        if not await self.branch_repo.deactivate_branch(branch_id):
            raise ValueError(f"Branch with id {branch_id} not found")


class BranchHoursAdminUseCase:
    """Administration use cases for branch hours."""

    def __init__(
        self,
        branch_repo: BranchRepository,
        schedule_repo: ScheduleRepository,
    ):
        self.branch_repo = branch_repo
        self.schedule_repo = schedule_repo

    async def list_hours(
        self, branch_id: int, user_id: Optional[int]
    ) -> List[Schedule]:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        return await self.schedule_repo.list_branch_hours(branch_id)

    async def create_hour(
        self, branch_id: int, data: dict, user_id: Optional[int]
    ) -> Schedule:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        payload = _clean_payload(data)
        _validate_schedule_payload(payload)
        return await self.schedule_repo.create_schedule(branch_id, payload)

    async def update_hour(
        self,
        branch_id: int,
        hour_id: int,
        data: dict,
        user_id: Optional[int],
    ) -> Schedule:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        payload = _clean_payload(data)
        current = await self.schedule_repo.get_schedule_by_id(branch_id, hour_id)
        if not current:
            raise ValueError(f"Schedule with id {hour_id} not found")
        merged = current.model_dump() | payload
        _validate_schedule_payload(merged)
        schedule = await self.schedule_repo.update_schedule(branch_id, hour_id, payload)
        if not schedule:
            raise ValueError(f"Schedule with id {hour_id} not found")
        return schedule

    async def delete_hour(
        self, branch_id: int, hour_id: int, user_id: Optional[int]
    ) -> None:
        user_id = _ensure_authenticated(user_id)
        if not await self.branch_repo.is_branch_accessible(branch_id, user_id):
            raise ValueError("Access denied to branch")
        if not await self.schedule_repo.delete_schedule(branch_id, hour_id):
            raise ValueError(f"Schedule with id {hour_id} not found")
