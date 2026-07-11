"""Dependency injection helpers for API routers."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.clinic_use_case import (
    BranchAdminUseCase,
    BranchHoursAdminUseCase,
    ClinicAdminUseCase,
    GetBranchProfileUseCase,
    GetBranchProfileWithPermissionUseCase,
)
from app.application.use_cases.internal_user_use_case import InternalUserUseCase
from app.application.use_cases.service_use_case import ServiceUseCase
from app.application.use_cases.veterinarian_use_case import VeterinarianUseCase
from app.domain.repositories.clinic_repository import (
    BranchRepository,
    ClinicRepository,
    RatingRepository,
    ScheduleRepository,
)
from app.domain.repositories.clinic_repository import (
    ServiceRepository as ClinicServiceRepository,
)
from app.domain.repositories.internal_user_repo import InternalUserRepository
from app.domain.repositories.service_repo import ServiceRepository
from app.domain.repositories.veterinarian_repo import VeterinarianRepository
from app.infrastructure.database import get_db


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


def _make_clinic_service_repo(db: Session) -> ClinicServiceRepository:
    from app.infrastructure.repositories.clinic_repository_impl import (
        ServiceRepositoryImpl,
    )

    return ServiceRepositoryImpl(db)


def _make_service_repo(db: Session) -> ServiceRepository:
    from app.infrastructure.database.repositories.service_repository_impl import (
        ServiceRepositoryImpl,
    )

    return ServiceRepositoryImpl(db)


def _make_veterinarian_repo(db: Session) -> VeterinarianRepository:
    from app.infrastructure.database.repositories.veterinarian_repository_impl import (
        VeterinarianRepositoryImpl,
    )

    return VeterinarianRepositoryImpl(db)


def _make_internal_user_repo(db: Session) -> InternalUserRepository:
    from app.infrastructure.database.repositories.internal_user_repository_impl import (
        InternalUserRepositoryImpl,
    )

    return InternalUserRepositoryImpl(db)


def get_branch_profile_use_case(
    db: Session = Depends(get_db),
) -> GetBranchProfileUseCase:
    """Dependency for public branch profile retrieval."""
    return GetBranchProfileUseCase(
        branch_repo=_make_branch_repo(db),
        service_repo=_make_clinic_service_repo(db),
        schedule_repo=_make_schedule_repo(db),
        rating_repo=_make_rating_repo(db),
    )


def get_branch_profile_with_permission_use_case(
    db: Session = Depends(get_db),
) -> GetBranchProfileWithPermissionUseCase:
    """Dependency for protected branch profile retrieval."""
    return GetBranchProfileWithPermissionUseCase(
        branch_repo=_make_branch_repo(db),
        service_repo=_make_clinic_service_repo(db),
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


def get_service_use_case(
    db: Session = Depends(get_db),
) -> ServiceUseCase:
    """Dependency for service use cases."""
    return ServiceUseCase(service_repository=_make_service_repo(db))


def get_veterinarian_use_case(
    db: Session = Depends(get_db),
) -> VeterinarianUseCase:
    """Dependency for veterinarian use cases."""
    return VeterinarianUseCase(veterinarian_repository=_make_veterinarian_repo(db))


def get_internal_user_use_case(
    db: Session = Depends(get_db),
) -> InternalUserUseCase:
    """Dependency for internal user use cases."""
    return InternalUserUseCase(internal_user_repository=_make_internal_user_repo(db))
