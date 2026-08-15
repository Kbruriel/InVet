"""Router FastAPI para servicios (slice 006)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.service_schemas import (
    ServiceCreateSchema,
    ServiceListSchema,
    ServiceReadSchema,
    ServiceUpdateSchema,
)
from app.application.use_cases.service_use_cases import (
    CreateServiceUseCase,
    DeactivateServiceUseCase,
    GetServiceUseCase,
    ListServicesUseCase,
    UpdateServiceUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.slice006_repositories import ServiceRepository
from app.infrastructure.database.repositories.service_repository_impl import (
    ServiceRepositoryImpl,
)


def get_current_db() -> Session:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    return next(_get_db())


router = APIRouter(prefix="/services", tags=["services"])


def get_service_repo(db: Session = Depends(get_current_db)) -> ServiceRepository:
    """Dependencia para el repositorio de servicios (devuelve interfaz ABC)."""
    return ServiceRepositoryImpl(db)


@router.post(
    "",
    response_model=ServiceReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear servicio",
)
async def create_service(
    body: ServiceCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: ServiceRepository = Depends(get_service_repo),
) -> ServiceReadSchema:
    """Crear un nuevo servicio.

    Solo usuarios con rol admin o manager pueden crear servicios.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    try:
        use_case = CreateServiceUseCase(repo)
        service = await use_case.execute(body.model_dump(), clinic_id)
        return ServiceReadSchema.model_validate(service)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=ServiceListSchema,
    summary="Listar servicios",
)
async def list_services(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página (máx 100)"),
    is_active: bool = Query(True, description="Filtrar solo activos"),
    current_user: dict = Depends(get_current_access_user),
    repo: ServiceRepositoryImpl = Depends(get_service_repo),
) -> ServiceListSchema:
    """Listar servicios del tenant con paginación."""
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = ListServicesUseCase(repo)
    items, total = await use_case.execute(
        clinic_id, page, size, is_active_only=is_active
    )

    return ServiceListSchema(
        items=[ServiceReadSchema.model_validate(s) for s in items],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceReadSchema,
    summary="Obtener servicio",
)
async def get_service(
    service_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: ServiceRepositoryImpl = Depends(get_service_repo),
) -> ServiceReadSchema:
    """Obtener un servicio por ID con tenant isolation."""
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = GetServiceUseCase(repo)
    service = await use_case.execute(service_id, clinic_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado.",
        )

    # Verificar ownership (tenant isolation / IDOR protection)
    if service.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este servicio.",
        )

    return ServiceReadSchema.model_validate(service)


@router.put(
    "/{service_id}",
    response_model=ServiceReadSchema,
    summary="Actualizar servicio",
)
async def update_service(
    service_id: int,
    body: ServiceUpdateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: ServiceRepositoryImpl = Depends(get_service_repo),
) -> ServiceReadSchema:
    """Actualizar un servicio existente."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = UpdateServiceUseCase(repo)
    service = await use_case.execute(service_id, clinic_id, body.model_dump())

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado.",
        )

    # Verificar ownership
    if service.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este servicio.",
        )

    return ServiceReadSchema.model_validate(service)


@router.patch(
    "/{service_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar servicio",
)
async def deactivate_service(
    service_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: ServiceRepositoryImpl = Depends(get_service_repo),
) -> None:
    """Desactivar un servicio por ID."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = DeactivateServiceUseCase(repo)
    service = await use_case.execute(service_id, clinic_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado.",
        )

    # Verificar ownership
    if service.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este servicio.",
        )


def _get_clinic_id_from_user(current_user: dict) -> int:
    """Extraer clinic_id del usuario autenticado.

    En un sistema real, esto vendría del token JWT o de una tabla de mapeo.
    Para este slice, se asume que el usuario pertenece a una clínica.
    """
    clinic_id = current_user.get("clinic_id")
    if clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo determinar la clínica del usuario.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(clinic_id)
