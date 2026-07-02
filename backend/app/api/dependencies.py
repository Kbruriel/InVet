"""Dependency injection for clinic related services."""
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from app.application.use_cases.clinic_use_case import GetBranchProfileUseCase, GetBranchProfileWithPermissionUseCase
from app.infrastructure.repositories.clinic_repository_impl import BranchRepositoryImpl, ServiceRepositoryImpl, ScheduleRepositoryImpl, RatingRepositoryImpl
from app.infrastructure.database import get_db


def get_branch_profile_use_case(
    db: Session = Depends(get_db)
) -> GetBranchProfileUseCase:
    """Dependency for branch profile use case with injected repositories."""
    branch_repo = BranchRepositoryImpl(db)
    service_repo = ServiceRepositoryImpl(db)
    schedule_repo = ScheduleRepositoryImpl(db)
    rating_repo = RatingRepositoryImpl(db)
    
    return GetBranchProfileUseCase(
        branch_repo=branch_repo,
        service_repo=service_repo,
        schedule_repo=schedule_repo,
        rating_repo=rating_repo
    )


def get_branch_profile_with_permission_use_case(
    db: Session = Depends(get_db)
) -> GetBranchProfileWithPermissionUseCase:
    """Dependency for branch profile use case with permission validation."""
    branch_repo = BranchRepositoryImpl(db)
    service_repo = ServiceRepositoryImpl(db)
    schedule_repo = ScheduleRepositoryImpl(db)
    rating_repo = RatingRepositoryImpl(db)
    
    return GetBranchProfileWithPermissionUseCase(
        branch_repo=branch_repo,
        service_repo=service_repo,
        schedule_repo=schedule_repo,
        rating_repo=rating_repo
    )