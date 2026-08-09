"""Router FastAPI para veterinarios (slice 006)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.veterinarian_schemas import (
    AssignmentSchema,
    VeterinarianCreateSchema,
    VeterinarianListSchema,
    VeterinarianReadSchema,
    VeterinarianUpdateSchema,
)
from app.application.use_cases.veterinarian_use_cases import (
    AssignServiceToVeterinarianUseCase,
    CreateVeterinarianUseCase,
    DeactivateVeterinarianUseCase,
    GetVeterinarianUseCase,
    ListVeterinariansUseCase,
    UnassignServiceFromVeterinarianUseCase,
    UpdateVeterinarianUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.slice006_repositories import (
    AssignmentRepository,
    ServiceRepository,
    VeterinarianRepository,
)
from app.infrastructure.database.repositories.assignment_repository_impl import (
    AssignmentRepositoryImpl,
)
from app.infrastructure.database.repositories.service_repository_impl import (
    ServiceRepositoryImpl,
)
from app.infrastructure.database.repositories.veterinarian_repository_impl import (
    VeterinarianRepositoryImpl,
)


def get_current_db() -> Session:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db
    return next(_get_db())


router = APIRouter(prefix="/veterinarians", tags=["veterinarians"])


def get_vet_repo(db: Session = Depends(get_current_db)) -> VeterinarianRepository:
    """Dependencia para el repositorio de veterinarios (devuelve interfaz ABC)."""
    return VeterinarianRepositoryImpl(db)


def get_service_repo(db: Session = Depends(get_current_db)) -> ServiceRepositoryImpl:
    """Dependencia para el repositorio de servicios."""
    return ServiceRepositoryImpl(db)


def get_assignment_repo(db: Session = Depends(get_current_db)) -> AssignmentRepositoryImpl:
    """Dependencia para el repositorio de asignaciones."""
    return AssignmentRepositoryImpl(db)


@router.post(
    "",
    response_model=VeterinarianReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear veterinario",
)
async def create_veterinarian(
    body: VeterinarianCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: VeterinarianRepository = Depends(get_vet_repo),
) -> VeterinarianReadSchema:
    """Crear un nuevo veterinario.

    Solo usuarios con rol admin o manager pueden crear veterinarios.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    try:
        use_case = CreateVeterinarianUseCase(repo)
        veterinarian = await use_case.execute(body.model_dump(), clinic_id)
        return VeterinarianReadSchema.model_validate(veterinarian)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=VeterinarianListSchema,
    summary="Listar veterinarios",
)
async def list_veterinarians(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página (máx 100)"),
    is_active: bool = Query(True, description="Filtrar solo activos"),
    current_user: dict = Depends(get_current_access_user),
    repo: VeterinarianRepository = Depends(get_vet_repo),
) -> VeterinarianListSchema:
    """Listar veterinarios del tenant con paginación."""
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = ListVeterinariansUseCase(repo)
    items, total = await use_case.execute(
        clinic_id, page, size, is_active_only=is_active
    )

    return VeterinarianListSchema(
        items=[VeterinarianReadSchema.model_validate(v) for v in items],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{vet_id}",
    response_model=VeterinarianReadSchema,
    summary="Obtener veterinario",
)
async def get_veterinarian(
    vet_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: VeterinarianRepository = Depends(get_vet_repo),
) -> VeterinarianReadSchema:
    """Obtener un veterinario por ID con tenant isolation."""
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = GetVeterinarianUseCase(repo)
    veterinarian = await use_case.execute(vet_id, clinic_id)

    if veterinarian is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado.",
        )

    # Verificar ownership (tenant isolation / IDOR protection)
    if veterinarian.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este veterinario.",
        )

    return VeterinarianReadSchema.model_validate(veterinarian)


@router.put(
    "/{vet_id}",
    response_model=VeterinarianReadSchema,
    summary="Actualizar veterinario",
)
async def update_veterinarian(
    vet_id: int,
    body: VeterinarianUpdateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: VeterinarianRepository = Depends(get_vet_repo),
) -> VeterinarianReadSchema:
    """Actualizar un veterinario existente."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = UpdateVeterinarianUseCase(repo)
    veterinarian = await use_case.execute(vet_id, clinic_id, body.model_dump())

    if veterinarian is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado.",
        )

    # Verificar ownership
    if veterinarian.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este veterinario.",
        )

    return VeterinarianReadSchema.model_validate(veterinarian)


@router.patch(
    "/{vet_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar veterinario",
)
async def deactivate_veterinarian(
    vet_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: VeterinarianRepository = Depends(get_vet_repo),
) -> None:
    """Desactivar un veterinario por ID."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = DeactivateVeterinarianUseCase(repo)
    veterinarian = await use_case.execute(vet_id, clinic_id)

    if veterinarian is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado.",
        )

    # Verificar ownership
    if veterinarian.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este veterinario.",
        )


@router.post(
    "/{vet_id}/assign-service",
    response_model=AssignmentSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Asignar servicio a veterinario",
)
async def assign_service_to_veterinarian(
    vet_id: int,
    body: dict,
    current_user: dict = Depends(get_current_access_user),
    assignment_repo: AssignmentRepositoryImpl = Depends(get_assignment_repo),
    service_repo: ServiceRepositoryImpl = Depends(get_service_repo),
) -> AssignmentSchema:
    """Asignar un servicio a un veterinario.

    Valida que ambos extremos pertenezcan al mismo clinic_id (tenant isolation).
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    service_id = body.get("service_id")
    if service_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'service_id' es obligatorio.",
        )

    # Validar que el servicio pertenece a la misma clínica
    service = await service_repo.get_service_by_id(service_id, clinic_id)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado en esta clínica.",
        )

    # Validar que el veterinario pertenece a la misma clínica
    vet_repo = VeterinarianRepositoryImpl(next(get_current_db()))
    veterinarian = await vet_repo.get_veterinarian_by_id(vet_id, clinic_id)
    if veterinarian is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado en esta clínica.",
        )

    try:
        use_case = AssignServiceToVeterinarianUseCase(assignment_repo, vet_repo)
        assignment = await use_case.execute(vet_id, service_id, clinic_id)
        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La asignación ya existe o los recursos no son válidos.",
            )
        return AssignmentSchema.model_validate(assignment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{vet_id}/assign-service/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desasignar servicio de veterinario",
)
async def unassign_service_from_veterinarian(
    vet_id: int,
    service_id: int,
    current_user: dict = Depends(get_current_access_user),
    assignment_repo: AssignmentRepositoryImpl = Depends(get_assignment_repo),
) -> None:
    """Desasignar un servicio de un veterinario."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = UnassignServiceFromVeterinarianUseCase(assignment_repo)
    success = await use_case.execute(vet_id, service_id, clinic_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asignación no encontrada.",
        )


def _get_clinic_id_from_user(current_user: dict) -> int:
    """Extraer clinic_id del usuario autenticado."""
    clinic_id = current_user.get("clinic_id")
    if clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo determinar la clínica del usuario.",
        )
    return int(clinic_id)
