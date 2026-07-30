"""Router para propietarios."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.clinic_router import get_current_user
from app.api.schemas.clinic_schemas import PaginationMeta
from app.api.schemas.owner_schema import (
    Owner,
    OwnerCreate,
    OwnerUpdate,
    PaginatedOwnersResponse,
)
from app.application.use_cases.owner_use_case import OwnerUseCase
from app.domain.repositories.owner_repository import OwnerRepository
from app.domain.repositories.pet_repository import PetRepository
from app.infrastructure.database.models.owner import Owner as OwnerDB
from app.infrastructure.database.models.user import User as UserDB
from app.infrastructure.database.repositories.owner_repository_impl import (
    OwnerRepositoryImpl,
)
from app.infrastructure.database.repositories.pet_repository_impl import (
    PetRepositoryImpl,
)
from app.infrastructure.database.session import get_db
from app.infrastructure.models.clinic_models import ClinicDB

router = APIRouter(prefix="/owners", tags=["owners"])


def get_owner_repository(db: Session = Depends(get_db)) -> OwnerRepository:
    """Inyeccion de dependencia para el repositorio de propietarios."""
    return OwnerRepositoryImpl(db)


def get_pet_repository(db: Session = Depends(get_db)) -> PetRepository:
    """Inyeccion de dependencia para el repositorio de mascotas."""
    return PetRepositoryImpl(db)


def get_owner_use_case(
    repository: OwnerRepository = Depends(get_owner_repository),
    pet_repository: PetRepository = Depends(get_pet_repository),
) -> OwnerUseCase:
    """Inyeccion de dependencia para el caso de uso de propietarios."""
    return OwnerUseCase(repository, pet_repository)


def _accessible_clinic_ids(db: Session, user_id: int) -> list[int]:
    user = (
        db.query(UserDB).filter(UserDB.id == user_id, UserDB.is_active == True).first()
    )
    if not user:
        return []
    if getattr(user, "is_admin", False):
        return [clinic_id for (clinic_id,) in db.query(ClinicDB.id).all()]
    return [
        clinic_id
        for (clinic_id,) in (
            db.query(OwnerDB.clinic_id)
            .filter(
                OwnerDB.email == user.email,
                OwnerDB.is_active == True,
                OwnerDB.clinic_id.isnot(None),
            )
            .all()
        )
    ]


def _ensure_owner_access(db: Session, current_user_id: int, owner: OwnerDB) -> None:
    if owner.clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Propietario sin clinica asignada",
        )
    if owner.clinic_id not in _accessible_clinic_ids(db, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este propietario",
        )


@router.get("/", response_model=PaginatedOwnersResponse)
async def get_owners(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    clinic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: OwnerUseCase = Depends(get_owner_use_case),
):
    """Obtiene una lista paginada de propietarios."""
    accessible_ids = _accessible_clinic_ids(db, current_user["id"])
    if clinic_id is not None:
        if clinic_id not in accessible_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para acceder a esa clinica",
            )
        clinic_ids = [clinic_id]
    else:
        clinic_ids = accessible_ids

    owners = []
    for accessible_clinic_id in clinic_ids:
        owners.extend(use_case.get_owners_by_clinic(accessible_clinic_id, 0, None))

    owners = sorted(owners, key=lambda owner: int(owner.id))
    total = len(owners)
    items = owners[skip : skip + limit]
    return PaginatedOwnersResponse(
        items=[Owner.model_validate(owner) for owner in items],
        pagination=PaginationMeta(skip=skip, limit=limit, total=total),
    )


@router.get("/{owner_id}", response_model=Owner)
async def get_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: OwnerUseCase = Depends(get_owner_use_case),
):
    """Obtiene un propietario por ID."""
    owner = use_case.get_owner(owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado"
        )
    _ensure_owner_access(db, current_user["id"], owner)
    return owner


@router.post("/", response_model=Owner, status_code=status.HTTP_201_CREATED)
async def create_owner(
    owner: OwnerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: OwnerUseCase = Depends(get_owner_use_case),
):
    """Crea un nuevo propietario."""
    if owner.clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="clinic_id es requerido",
        )
    if owner.clinic_id not in _accessible_clinic_ids(db, current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear propietarios en esa clinica",
        )
    return use_case.create_owner(owner.model_dump())


@router.put("/{owner_id}", response_model=Owner)
async def update_owner(
    owner_id: int,
    owner: OwnerUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: OwnerUseCase = Depends(get_owner_use_case),
):
    """Actualiza un propietario existente."""
    existing_owner = use_case.get_owner(owner_id)
    if not existing_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado"
        )
    _ensure_owner_access(db, current_user["id"], existing_owner)

    payload = owner.model_dump(exclude_unset=True)
    target_clinic_id = payload.get("clinic_id", existing_owner.clinic_id)
    if target_clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="clinic_id es requerido",
        )
    if target_clinic_id not in _accessible_clinic_ids(db, current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para mover propietarios a esa clinica",
        )

    updated_owner = use_case.update_owner(owner_id, payload)
    if not updated_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado"
        )
    return updated_owner


@router.delete("/{owner_id}", response_model=dict)
async def delete_owner(
    owner_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: OwnerUseCase = Depends(get_owner_use_case),
):
    """Elimina un propietario."""
    owner = use_case.get_owner(owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado"
        )
    _ensure_owner_access(db, current_user["id"], owner)

    try:
        success = use_case.delete_owner(owner_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado"
        )
    return {"message": "Propietario eliminado correctamente"}
