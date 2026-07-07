"""Dependency injection for clinic related services."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.clinic_use_case import (
    BranchAdminUseCase,
    BranchHoursAdminUseCase,
    ClinicAdminUseCase,
    GetBranchProfileUseCase,
    GetBranchProfileWithPermissionUseCase,
)
from app.domain.repositories.clinic_repository import (
    BranchRepository,
    ClinicRepository,
    RatingRepository,
    ScheduleRepository,
    ServiceRepository,
)
from app.infrastructure.database import get_db

# ---------------------------------------------------------------------------
# Factory — centralises instantiation of infrastructure concrete classes.
# The public API of this module exposes only interfaces so that routers and
# use-cases remain decoupled from the storage layer.
# ---------------------------------------------------------------------------


def _make_branch_repo(db: Session) -> BranchRepository:
    from app.infrastructure.repositories.clinic_repository_impl import (
        BranchRepositoryImpl,
    )

    return BranchRepositoryImpl(db)


def _make_clinic_repo(db: Session) -> ClinicRepository:
    from app.infrastructure.repositories.clinic_repository_impl import (
        ClinicRepositoryImpl,
    )

    return ClinicRepositoryImpl(db)


def _make_rating_repo(db: Session) -> RatingRepository:
    from app.infrastructure.repositories.clinic_repository_impl import (
        RatingRepositoryImpl,
    )

    return RatingRepositoryImpl(db)


def _make_schedule_repo(db: Session) -> ScheduleRepository:
    from app.infrastructure.repositories.clinic_repository_impl import (
        ScheduleRepositoryImpl,
    )

    return ScheduleRepositoryImpl(db)


def _make_service_repo(db: Session) -> ServiceRepository:
    from app.infrastructure.repositories.clinic_repository_impl import (
        ServiceRepositoryImpl,
    )

    return ServiceRepositoryImpl(db)


# ---------------------------------------------------------------------------
# FastAPI-dependent / public dependencys -- signatures accept pure interfaces.
# ---------------------------------------------------------------------------


def get_branch_profile_use_case(
    db: Session = Depends(get_db),
) -> GetBranchProfileUseCase:
    """Dependency for public branch profile retrieval."""
    return GetBranchProfileUseCase(
        branch_repo=_make_branch_repo(db),
        service_repo=_make_service_repo(db),
        schedule_repo=_make_schedule_repo(db),
        rating_repo=_make_rating_repo(db),
    )


def get_branch_profile_with_permission_use_case(
    db: Session = Depends(get_db),
) -> GetBranchProfileWithPermissionUseCase:
    """Dependency for protected branch profile retrieval."""
    return GetBranchProfileWithPermissionUseCase(
        branch_repo=_make_branch_repo(db),
        service_repo=_make_service_repo(db),
        schedule_repo=_make_schedule_repo(db),
        rating_repo=_make_rating_repo(db),
    )


def get_clinic_admin_use_case(
    db: Session = Depends(get_db),
) -> ClinicAdminUseCase:
    """Dependency for clinic administration use cases."""
    return ClinicAdminUseCase(clinic_repo=_make_clinic_repo(db))


def get_branch_admin_use_case(
    db: Session = Depends(get_db),
) -> BranchAdminUseCase:
    """Dependency for branch administration use cases."""
    return BranchAdminUseCase(
        branch_repo=_make_branch_repo(db),
        clinic_repo=_make_clinic_repo(db),
    )


def get_branch_hours_admin_use_case(
    db: Session = Depends(get_db),
) -> BranchHoursAdminUseCase:
    """Dependency for branch hours administration use cases."""
    return BranchHoursAdminUseCase(
        branch_repo=_make_branch_repo(db),
        schedule_repo=_make_schedule_repo(db),
    )
