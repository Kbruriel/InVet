"""Router FastAPI para mascotas (slice 007).

Este módulo expone dos routers separados:
- `owner_pets_router`: endpoints relacionados a mascotas desde la perspectiva del `owner` (prefijo `/owners`).
- `pet_router`: endpoints generales por `pet_id` (prefijo `/pets`).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.owner_pets_schemas import (
    PetCreateSchema,
    PetHistoryEntrySchema,
    PetHistoryListSchema,
    PetListSchema,
    PetReadSchema,
    PetUpdateSchema,
)
from app.application.use_cases.owner_pets_use_cases import (
    CreatePetUseCase,
    DeletePetUseCase,
    GetOwnerByUserIdUseCase,
    GetPetHistoryUseCase,
    GetPetUseCase,
    ListPetsByOwnerUseCase,
    UpdatePetUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.owner_repository import PetRepository


def get_current_db() -> Session:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    return next(_get_db())


# Routers: uno para rutas bajo /owners, otro para las rutas bajo /pets
owner_pets_router = APIRouter(prefix="/owners", tags=["pets"])
pet_router = APIRouter(prefix="/pets", tags=["pets"])


def get_pet_repo(db: Session = Depends(get_current_db)) -> PetRepository:
    """Dependencia para el repositorio de mascotas (devuelve interfaz ABC)."""
    # Use factory to obtain concrete implementation; keeps router decoupled from impl.
    from app.infrastructure.database.repositories.factory import get_pet_repo as _get

    return _get(db)


def get_owner_repo(db: Session = Depends(get_current_db)):
    """Dependencia para el repositorio de propietarios."""
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


def _authorize_pet_access(
    pet_owner_id: int,
    owner_id: int | None,
    user_role: str,
    *,
    allow_clinic: bool = False,
) -> None:
    """Validar que el usuario tiene permiso para acceder a la mascota."""
    if user_role == "admin":
        return

    if allow_clinic and user_role == "clinic":
        return

    if pet_owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso.",
        )


def _get_current_owner_id(
    current_user: dict,
    owner_repo,
) -> int | None:
    """Obtener el id del owner asociado al usuario autenticado."""
    user_id = _get_user_id_from_user(current_user)
    use_case = GetOwnerByUserIdUseCase(owner_repo)
    owner = use_case.execute(user_id)
    if not owner:
        return None
    return owner.id


# ---------------------------------------------------------------------------
# Endpoints de mascotas por owner (owners/me/pets)
# ---------------------------------------------------------------------------


@owner_pets_router.get(
    "/me/pets",
    response_model=PetListSchema,
    summary="Listar mascotas propias",
)
def list_my_pets(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(
        20, ge=1, le=100, alias="page_size", description="Tamaño de página (máx 100)"
    ),
    current_user: dict = Depends(get_current_access_user),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo=Depends(get_owner_repo),
) -> PetListSchema:
    """Listar mascotas del propietario autenticado con paginación."""
    owner_id = _get_current_owner_id(current_user, owner_repo)
    if owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de propietario vinculado a este usuario.",
        )

    use_case = ListPetsByOwnerUseCase(pet_repo)
    items, total = use_case.execute(owner_id, page, page_size)

    return PetListSchema(
        items=[PetReadSchema.model_validate(p) for p in items],
        meta={
            "page": page,
            "page_size": page_size,
            "size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    )


@owner_pets_router.post(
    "/me/pets",
    response_model=PetReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar mascota",
)
def create_my_pet(
    body: PetCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo=Depends(get_owner_repo),
) -> PetReadSchema:
    """Registrar una nueva mascota vinculada al propietario autenticado."""
    owner_id = _get_current_owner_id(current_user, owner_repo)
    if owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de propietario vinculado a este usuario.",
        )

    try:
        use_case = CreatePetUseCase(pet_repo)
        pet = use_case.execute(body, owner_id)
        return PetReadSchema.model_validate(pet)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Endpoints de mascotas por ID (pets/{pet_id})
# ---------------------------------------------------------------------------


@pet_router.get(
    "/{pet_id}",
    response_model=PetReadSchema,
    summary="Obtener mascota",
)
def get_pet(
    pet_id: int,
    current_user: dict = Depends(get_current_access_user),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo=Depends(get_owner_repo),
) -> PetReadSchema:
    """Obtener una mascota por ID con validación de ownership."""
    owner_id = _get_current_owner_id(current_user, owner_repo)
    user_role = current_user.get("role", "user")

    use_case = GetPetUseCase(pet_repo)
    pet = use_case.execute(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la mascota solicitada.",
        )

    _authorize_pet_access(pet.owner_id, owner_id, user_role, allow_clinic=True)

    return PetReadSchema.model_validate(pet)


@pet_router.put(
    "/{pet_id}",
    response_model=PetReadSchema,
    summary="Actualizar mascota",
)
def update_pet(
    pet_id: int,
    body: PetUpdateSchema,
    current_user: dict = Depends(get_current_access_user),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo=Depends(get_owner_repo),
) -> PetReadSchema:
    """Actualizar una mascota con validación de ownership."""
    owner_id = _get_current_owner_id(current_user, owner_repo)
    user_role = current_user.get("role", "user")

    # Obtener pet actual
    get_pet = GetPetUseCase(pet_repo)
    pet = get_pet.execute(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la mascota solicitada.",
        )

    _authorize_pet_access(pet.owner_id, owner_id, user_role)

    try:
        use_case = UpdatePetUseCase(pet_repo)
        updated_pet = use_case.execute(pet_id, body)
        if not updated_pet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo actualizar la mascota.",
            )
        return PetReadSchema.model_validate(updated_pet)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@pet_router.delete(
    "/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar mascota",
)
def delete_pet(
    pet_id: int,
    current_user: dict = Depends(get_current_access_user),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo=Depends(get_owner_repo),
) -> None:
    """Eliminar una mascota con validación de ownership."""
    owner_id = _get_current_owner_id(current_user, owner_repo)
    user_role = current_user.get("role", "user")

    # Obtener pet actual
    get_pet = GetPetUseCase(pet_repo)
    pet = get_pet.execute(pet_id)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la mascota solicitada.")

    _authorize_pet_access(pet.owner_id, owner_id, user_role)

    use_case = DeletePetUseCase(pet_repo)
    use_case.execute(pet_id)
    return None


@pet_router.get(
    "/{pet_id}/history",
    response_model=PetHistoryListSchema,
    summary="Obtener historial de mascota",
)
def pet_history(
    pet_id: int,
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(
        20, ge=1, le=100, alias="page_size", description="Tamaño de página (máx 100)"
    ),
    current_user: dict = Depends(get_current_access_user),
    owner_repo=Depends(get_owner_repo),
    pet_repo: PetRepository = Depends(get_pet_repo),
) -> PetHistoryListSchema:
    owner_id = _get_current_owner_id(current_user, owner_repo)
    user_role = current_user.get("role", "user")

    # Ensure pet exists and validate ownership even if history is empty
    get_pet_uc = GetPetUseCase(pet_repo)
    pet = get_pet_uc.execute(pet_id)
    if not pet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró la mascota solicitada.")

    _authorize_pet_access(pet.owner_id, owner_id, user_role, allow_clinic=True)

    use_case = GetPetHistoryUseCase(pet_repo)
    items, total = use_case.execute(pet_id, page, page_size)
    return PetHistoryListSchema(
        items=[PetHistoryEntrySchema.model_validate(i) for i in items],
        meta={
            "page": page,
            "page_size": page_size,
            "size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    )
