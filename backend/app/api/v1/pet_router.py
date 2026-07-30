"""Router para mascotas."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.clinic_router import get_current_user
from app.api.schemas.clinic_schemas import PaginationMeta
from app.api.schemas.pet_schema import PaginatedPetsResponse, Pet, PetCreate, PetUpdate
from app.application.use_cases.pet_use_case import PetUseCase
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

router = APIRouter(prefix="/pets", tags=["pets"])


def get_pet_repository(db: Session = Depends(get_db)) -> PetRepository:
    """Inyeccion de dependencia para el repositorio de mascotas."""
    return PetRepositoryImpl(db)


def get_pet_use_case(
    repository: PetRepository = Depends(get_pet_repository),
) -> PetUseCase:
    """Inyeccion de dependencia para el caso de uso de mascotas."""
    return PetUseCase(repository)


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


def _get_owner_or_404(db: Session, owner_id: int) -> OwnerDB:
    owner = OwnerRepositoryImpl(db).get_owner(owner_id)
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado"
        )
    return owner


def _ensure_owner_access(db: Session, current_user_id: int, owner: OwnerDB) -> None:
    if owner.clinic_id is None or owner.clinic_id not in _accessible_clinic_ids(
        db, current_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta mascota",
        )


@router.get("/", response_model=PaginatedPetsResponse)
async def get_pets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    owner_id: Optional[int] = None,
    breed: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: PetUseCase = Depends(get_pet_use_case),
):
    """Obtiene una lista paginada de mascotas."""
    accessible_clinic_ids = _accessible_clinic_ids(db, current_user["id"])
    owner_repo = OwnerRepositoryImpl(db)

    if owner_id is not None:
        owner = _get_owner_or_404(db, int(owner_id))
        _ensure_owner_access(db, current_user["id"], owner)
        owners = [owner]
    else:
        owners = []
        for clinic_id in accessible_clinic_ids:
            owners.extend(owner_repo.get_owners_by_clinic(clinic_id, 0, None))

    pets = []
    for owner in owners:
        pets.extend(use_case.get_pets_by_owner(int(owner.id), 0, None))

    if breed is not None:
        pets = [pet for pet in pets if pet.breed == breed]

    pets = sorted(pets, key=lambda pet: int(pet.id))
    total = len(pets)
    items = pets[skip : skip + limit]
    return PaginatedPetsResponse(
        items=[Pet.model_validate(pet) for pet in items],
        pagination=PaginationMeta(skip=skip, limit=limit, total=total),
    )


@router.get("/{pet_id}", response_model=Pet)
async def get_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: PetUseCase = Depends(get_pet_use_case),
):
    """Obtiene una mascota por ID."""
    pet = use_case.get_pet(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    owner = _get_owner_or_404(db, int(pet.owner_id))
    _ensure_owner_access(db, current_user["id"], owner)
    return pet


@router.post("/", response_model=Pet, status_code=status.HTTP_201_CREATED)
async def create_pet(
    pet: PetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: PetUseCase = Depends(get_pet_use_case),
):
    """Crea una nueva mascota."""
    owner = _get_owner_or_404(db, pet.owner_id)
    _ensure_owner_access(db, current_user["id"], owner)
    return use_case.create_pet(pet.model_dump())


@router.put("/{pet_id}", response_model=Pet)
async def update_pet(
    pet_id: int,
    pet: PetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: PetUseCase = Depends(get_pet_use_case),
):
    """Actualiza una mascota existente."""
    existing_pet = use_case.get_pet(pet_id)
    if not existing_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    owner = _get_owner_or_404(db, int(existing_pet.owner_id))
    _ensure_owner_access(db, current_user["id"], owner)

    payload = pet.model_dump(exclude_unset=True)
    if "owner_id" in payload:
        new_owner = _get_owner_or_404(db, int(payload["owner_id"]))
        _ensure_owner_access(db, current_user["id"], new_owner)

    updated_pet = use_case.update_pet(pet_id, payload)
    if not updated_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    return updated_pet


@router.delete("/{pet_id}", response_model=dict)
async def delete_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    use_case: PetUseCase = Depends(get_pet_use_case),
):
    """Elimina una mascota."""
    existing_pet = use_case.get_pet(pet_id)
    if not existing_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    owner = _get_owner_or_404(db, int(existing_pet.owner_id))
    _ensure_owner_access(db, current_user["id"], owner)

    try:
        success = use_case.delete_pet(pet_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    return {"message": "Mascota eliminada correctamente"}
