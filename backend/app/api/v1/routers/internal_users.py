"""Router FastAPI para usuarios internos (slice 006)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.internal_user_schemas import (
    InternalUserCreateSchema,
    InternalUserListSchema,
    InternalUserReadSchema,
    InternalUserUpdateSchema,
)
from app.application.use_cases.internal_user_use_cases import (
    AssignBranchToInternalUserUseCase,
    CreateInternalUserUseCase,
    DeactivateInternalUserUseCase,
    GetInternalUserUseCase,
    ListInternalUsersUseCase,
    UnassignBranchFromInternalUserUseCase,
    UpdateInternalUserUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.slice006_repositories import InternalUserRepository
from app.infrastructure.database.repositories.internal_user_repository_impl import (
    InternalUserRepositoryImpl,
)


def get_current_db() -> Session:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    return next(_get_db())


router = APIRouter(prefix="/internal-users", tags=["internal-users"])


def get_internal_user_repo(
    db: Session = Depends(get_current_db),
) -> InternalUserRepository:
    """Dependencia para el repositorio de usuarios internos (devuelve interfaz ABC)."""
    return InternalUserRepositoryImpl(db)


@router.post(
    "",
    response_model=InternalUserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario interno",
)
async def create_internal_user(
    body: InternalUserCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> InternalUserReadSchema:
    """Crear un nuevo usuario interno.

    Solo usuarios con rol admin o manager pueden crear usuarios internos.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    try:
        use_case = CreateInternalUserUseCase(repo, db=get_current_db())
        internal_user = await use_case.execute(body.model_dump(), clinic_id)
        return InternalUserReadSchema.model_validate(internal_user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=InternalUserListSchema,
    summary="Listar usuarios internos",
)
async def list_internal_users(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página (máx 100)"),
    is_active: bool = Query(True, description="Filtrar solo activos"),
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> InternalUserListSchema:
    """Listar usuarios internos del tenant con paginación."""
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = ListInternalUsersUseCase(repo)
    items, total = await use_case.execute(
        clinic_id, page, size, is_active_only=is_active
    )

    return InternalUserListSchema(
        items=[InternalUserReadSchema.model_validate(u) for u in items],
        total=total,
        page=page,
        size=size,
    )


@router.get(
    "/{user_id}",
    response_model=InternalUserReadSchema,
    summary="Obtener usuario interno",
)
async def get_internal_user(
    user_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> InternalUserReadSchema:
    """Obtener un usuario interno por ID con tenant isolation."""
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = GetInternalUserUseCase(repo)
    internal_user = await use_case.execute(user_id, clinic_id)

    if internal_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado.",
        )

    # Verificar ownership (tenant isolation / IDOR protection)
    if internal_user.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este usuario interno.",
        )

    return InternalUserReadSchema.model_validate(internal_user)


@router.put(
    "/{user_id}",
    response_model=InternalUserReadSchema,
    summary="Actualizar usuario interno",
)
async def update_internal_user(
    user_id: int,
    body: InternalUserUpdateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> InternalUserReadSchema:
    """Actualizar un usuario interno existente."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = UpdateInternalUserUseCase(repo)
    internal_user = await use_case.execute(user_id, clinic_id, body.model_dump())

    if internal_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado.",
        )

    # Verificar ownership
    if internal_user.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este usuario interno.",
        )

    return InternalUserReadSchema.model_validate(internal_user)


@router.patch(
    "/{user_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar usuario interno",
)
async def deactivate_internal_user(
    user_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> None:
    """Desactivar un usuario interno por ID."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = DeactivateInternalUserUseCase(repo)
    internal_user = await use_case.execute(user_id, clinic_id)

    if internal_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado.",
        )

    # Verificar ownership
    if internal_user.clinic_id != clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este usuario interno.",
        )


@router.post(
    "/{user_id}/assign-branch",
    response_model=InternalUserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Asignar sucursal a usuario interno",
)
async def assign_branch_to_internal_user(
    user_id: int,
    body: dict,
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> InternalUserReadSchema:
    """Asignar una sucursal a un usuario interno."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    branch_id = body.get("branch_id")
    if branch_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'branch_id' es obligatorio.",
        )

    use_case = AssignBranchToInternalUserUseCase(repo)
    internal_user = await use_case.execute(user_id, clinic_id, int(branch_id))

    if internal_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado.",
        )

    return InternalUserReadSchema.model_validate(internal_user)


@router.delete(
    "/{user_id}/assign-branch/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desasignar sucursal de usuario interno",
)
async def unassign_branch_from_internal_user(
    user_id: int,
    branch_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> None:
    """Desasignar una sucursal de un usuario interno."""
    clinic_id = _get_clinic_id_from_user(current_user)
    role = current_user.get("role", "user")
    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado. Se requiere rol admin o manager.",
        )

    use_case = UnassignBranchFromInternalUserUseCase(repo)
    internal_user = await use_case.execute(user_id, clinic_id, branch_id)

    if internal_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado o sucursal no asignada.",
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
