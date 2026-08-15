"""Router FastAPI para propietarios (slice 007)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.owner_pets_schemas import (
    OwnerCreateSchema,
    OwnerReadSchema,
    OwnerUpdateSchema,
)
from app.application.use_cases.owner_pets_use_cases import (
    CreateOwnerUseCase,
    GetOwnerByUserIdUseCase,
    GetOwnerUseCase,
    UpdateOwnerUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.owner_repository import OwnerRepository


def get_current_db() -> Session:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    return next(_get_db())


router = APIRouter(prefix="/owners", tags=["owners"])


def get_owner_repo(db: Session = Depends(get_current_db)) -> OwnerRepository:
    """Dependencia para el repositorio de propietarios (devuelve interfaz ABC)."""
    from app.infrastructure.database.repositories.factory import get_owner_repo as _get

    return _get(db)


def _get_user_id_from_user(current_user: dict) -> int:
    """Extraer user_id del usuario autenticado."""
    user_id = current_user.get("user_id") or current_user.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado.",
        )
    return int(user_id)


@router.post(
    "",
    response_model=OwnerReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear perfil de propietario",
)
def create_owner(
    body: OwnerCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: OwnerRepository = Depends(get_owner_repo),
) -> OwnerReadSchema:
    """Crear un nuevo perfil de propietario.

    Solo usuarios autenticados pueden crear su perfil de propietario.
    """
    user_id = _get_user_id_from_user(current_user)

    # Verificar si ya existe un perfil para este usuario
    get_by_user_id = GetOwnerByUserIdUseCase(repo)
    existing = get_by_user_id.execute(user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un perfil de propietario vinculado a este usuario.",
        )

    try:
        use_case = CreateOwnerUseCase(repo)
        owner = use_case.execute(body, user_id)
        return OwnerReadSchema.model_validate(owner)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/me",
    response_model=OwnerReadSchema,
    summary="Obtener perfil propio",
)
def get_my_owner(
    current_user: dict = Depends(get_current_access_user),
    repo: OwnerRepository = Depends(get_owner_repo),
) -> OwnerReadSchema:
    """Obtener el perfil de propietario del usuario autenticado."""
    user_id = _get_user_id_from_user(current_user)

    use_case = GetOwnerByUserIdUseCase(repo)
    owner = use_case.execute(user_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de propietario vinculado a este usuario.",
        )
    return OwnerReadSchema.model_validate(owner)


@router.get(
    "/{owner_id}",
    response_model=OwnerReadSchema,
    summary="Obtener perfil por ID",
)
def get_owner(
    owner_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: OwnerRepository = Depends(get_owner_repo),
) -> OwnerReadSchema:
    """Obtener un perfil de propietario por ID."""
    current_user_id = _get_user_id_from_user(current_user)

    use_case = GetOwnerUseCase(repo)
    owner = use_case.execute(owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el perfil de propietario solicitado.",
        )

    # Validar que solo el propietario o admin pueda ver el perfil
    if owner.user_id != current_user_id and current_user.get("role") not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este perfil.",
        )

    return OwnerReadSchema.model_validate(owner)


@router.put(
    "/me",
    response_model=OwnerReadSchema,
    summary="Actualizar perfil propio",
)
def update_my_owner(
    body: OwnerUpdateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: OwnerRepository = Depends(get_owner_repo),
) -> OwnerReadSchema:
    """Actualizar el perfil de propietario del usuario autenticado."""
    user_id = _get_user_id_from_user(current_user)

    # Obtener el owner actual
    get_by_user_id = GetOwnerByUserIdUseCase(repo)
    owner = get_by_user_id.execute(user_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de propietario vinculado a este usuario.",
        )

    try:
        use_case = UpdateOwnerUseCase(repo)
        updated_owner = use_case.execute(owner.id, body)
        if not updated_owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo actualizar el perfil.",
            )
        return OwnerReadSchema.model_validate(updated_owner)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
