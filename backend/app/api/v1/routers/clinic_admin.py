"""Router FastAPI para administracion de clinicas (BE-005)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.v1.schemas.clinic_admin import (
    ClinicCreateSchema,
    ClinicListSchema,
    ClinicReadSchema,
    ClinicStatusSchema,
    ClinicUpdateSchema,
)
from app.application.use_cases.clinic_admin import (
    ActivateClinicUseCase,
    CreateClinicUseCase,
    DeactivateClinicUseCase,
    GetClinicUseCase,
    ListClinicsUseCase,
    UpdateClinicUseCase,
)
from app.infrastructure.database.repositories.clinic_repository_impl import (
    ClinicRepositoryImpl,
)

router = APIRouter(prefix="/api/v1/clinics", tags=["clinic-admin"])


def get_clinic_repo(db: Session = Depends(get_db)) -> ClinicRepositoryImpl:
    """Dependencia para el repositorio de clinicas."""
    return ClinicRepositoryImpl(db)


@router.post(
    "",
    response_model=ClinicReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear clinica",
)
async def create_clinic(
    body: ClinicCreateSchema,
    repo: ClinicRepositoryImpl = Depends(get_clinic_repo),
) -> ClinicReadSchema:
    """Crear una nueva clínica.

    Solo usuarios con rol clinic_admin pueden crear clínicas.
    """
    try:
        use_case = CreateClinicUseCase(repo)
        clinic = await use_case.execute(body.model_dump())
        return ClinicReadSchema.model_validate(clinic)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=ClinicListSchema,
    summary="Listar clinicas",
)
async def list_clinics(
    page: int = Query(1, ge=1, description="Numero de pagina"),
    size: int = Query(20, ge=1, le=100, description="Tamano de pagina (max 100)"),
    repo: ClinicRepositoryImpl = Depends(get_clinic_repo),
) -> ClinicListSchema:
    """Listar clínicas del tenant con paginación."""
    # TODO: Extraer tenant_id del token del usuario autenticado
    tenant_id = 1  # Placeholder hasta integrar auth por rol

    use_case = ListClinicsUseCase(repo)
    items, total = await use_case.execute(tenant_id, page, size)

    return ClinicListSchema(
        items=[ClinicReadSchema.model_validate(c) for c in items],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{clinic_id}",
    response_model=ClinicReadSchema,
    summary="Obtener clinica",
)
async def get_clinic(
    clinic_id: int,
    repo: ClinicRepositoryImpl = Depends(get_clinic_repo),
) -> ClinicReadSchema:
    """Obtener una clínica por ID."""
    use_case = GetClinicUseCase(repo)
    clinic = await use_case.execute(clinic_id)

    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinica no encontrada.",
        )

    return ClinicReadSchema.model_validate(clinic)

    return ClinicReadSchema.model_validate(clinic)


@router.put(
    "/{clinic_id}",
    response_model=ClinicReadSchema,
    summary="Actualizar clinica",
)
async def update_clinic(
    clinic_id: int,
    body: ClinicUpdateSchema,
    repo: ClinicRepositoryImpl = Depends(get_clinic_repo),
) -> ClinicReadSchema:
    """Actualizar una clínica existente."""
    try:
        use_case = UpdateClinicUseCase(repo)
        clinic = await use_case.execute(clinic_id, body.model_dump())

        if clinic is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clinica no encontrada.",
            )

        return ClinicReadSchema.model_validate(clinic)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{clinic_id}/status",
    response_model=ClinicReadSchema,
    summary="Cambiar estado de clinica",
)
async def change_clinic_status(
    clinic_id: int,
    body: ClinicStatusSchema,
    repo: ClinicRepositoryImpl = Depends(get_clinic_repo),
) -> ClinicReadSchema:
    """Inactivar o reactivar una clínica."""
    if body.active:
        use_case: ActivateClinicUseCase | DeactivateClinicUseCase = (
            ActivateClinicUseCase(repo)
        )
    else:
        use_case = DeactivateClinicUseCase(repo)

    clinic = await use_case.execute(clinic_id)  # type: ignore[union-attr]

    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinica no encontrada.",
        )

    return ClinicReadSchema.model_validate(clinic)
