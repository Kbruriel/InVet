"""Routers para perfiles de clínica/sucursal."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.branch_protected import BranchProtectedProfile
from app.api.v1.schemas.branch_public import BranchPublicProfile
from app.application.use_cases.branch_profile import (
    GetBranchProtectedProfileUseCase,
    GetBranchPublicProfileUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.branch_repository import (
    AvailabilitySummaryRepository,
    BranchRepository,
    BranchScheduleRepository,
    RatingSummaryRepository,
    ServiceRepository,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/clinics", tags=["branches"])


def get_branch_use_case(
    db: Session = Depends(get_db),
) -> GetBranchPublicProfileUseCase:
    """Inyección de dependencias para el caso de uso del perfil público."""
    from app.infrastructure.database.repositories.branch_repository import (
        AvailabilitySummaryRepositoryImpl,
        BranchRepositoryImpl,
        BranchScheduleRepositoryImpl,
        RatingSummaryRepositoryImpl,
        ServiceRepositoryImpl,
    )

    branch_repo: BranchRepository = BranchRepositoryImpl(db)
    service_repo: ServiceRepository = ServiceRepositoryImpl(db)
    schedule_repo: BranchScheduleRepository = BranchScheduleRepositoryImpl(db)
    rating_repo: RatingSummaryRepository = RatingSummaryRepositoryImpl(db)
    availability_repo: AvailabilitySummaryRepository = (
        AvailabilitySummaryRepositoryImpl(db)
    )

    return GetBranchPublicProfileUseCase(
        branch_repo, service_repo, schedule_repo, rating_repo, availability_repo
    )


def get_branch_protected_use_case(
    db: Session = Depends(get_db),
) -> GetBranchProtectedProfileUseCase:
    """Inyección de dependencias para el caso de uso del perfil protegido."""
    from app.infrastructure.database.repositories.branch_repository import (
        AvailabilitySummaryRepositoryImpl,
        BranchRepositoryImpl,
        BranchScheduleRepositoryImpl,
        RatingSummaryRepositoryImpl,
        ServiceRepositoryImpl,
    )

    branch_repo: BranchRepository = BranchRepositoryImpl(db)
    service_repo: ServiceRepository = ServiceRepositoryImpl(db)
    schedule_repo: BranchScheduleRepository = BranchScheduleRepositoryImpl(db)
    rating_repo: RatingSummaryRepository = RatingSummaryRepositoryImpl(db)
    availability_repo: AvailabilitySummaryRepository = (
        AvailabilitySummaryRepositoryImpl(db)
    )

    return GetBranchProtectedProfileUseCase(
        branch_repo, service_repo, schedule_repo, rating_repo, availability_repo
    )


@router.get("/branches/{branch_id}", response_model=BranchPublicProfile)
async def get_branch_public_profile(
    branch_id: int,
    use_case: GetBranchPublicProfileUseCase = Depends(get_branch_use_case),
) -> BranchPublicProfile:
    """Obtener perfil público de una sucursal (sin autenticación)."""
    branch = await use_case.execute(branch_id)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sucursal no encontrada"
        )

    return branch


@router.get("/branches/{clinic_id}/{branch_id}", response_model=BranchProtectedProfile)
async def get_branch_protected_profile(
    clinic_id: int,
    branch_id: int,
    use_case: GetBranchProtectedProfileUseCase = Depends(get_branch_protected_use_case),
    current_user: dict = Depends(get_current_access_user),
) -> BranchProtectedProfile:
    """Obtener perfil protegido de una sucursal (requiere autenticación y acceso).

    Ruta completa: GET /api/v1/clinics/branches/{clinic_id}/{branch_id}

    IDOR mitigation: Ambos casos (sucursal inexistente o sin permiso) devuelven 404
    para prevenir enumeracin de recursos.
    """
    branch = await use_case.execute(branch_id, clinic_id, current_user)
    if not branch:
        # Devolver 404 en lugar de 403 para prevenir IDOR
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    return branch
