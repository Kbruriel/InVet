"""Router para propietarios."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.owner_schema import Owner, OwnerCreate, OwnerUpdate
from app.application.use_cases.owner_use_case import OwnerUseCase
from app.core.database import get_db
from app.domain.repositories.owner_repository import OwnerRepository
from app.infrastructure.database.repositories.owner_repository_impl import OwnerRepositoryImpl

router = APIRouter(prefix="/owners", tags=["owners"])


def get_owner_repository(db: Session = Depends(get_db)) -> OwnerRepository:
    """Inyección de dependencia para el repositorio de propietarios."""
    return OwnerRepositoryImpl(db)


def get_owner_use_case(repository: OwnerRepository = Depends(get_owner_repository)) -> OwnerUseCase:
    """Inyección de dependencia para el caso de uso de propietarios."""
    return OwnerUseCase(repository)


@router.get("/", response_model=List[Owner])
async def get_owners(skip: int = 0, limit: int = 100, use_case: OwnerUseCase = Depends(get_owner_use_case)):
    """Obtiene una lista paginada de propietarios."""
    return use_case.get_owners(skip=skip, limit=limit)


@router.get("/{owner_id}", response_model=Owner)
async def get_owner(owner_id: int, use_case: OwnerUseCase = Depends(get_owner_use_case)):
    """Obtiene un propietario por ID."""
    owner = use_case.get_owner(owner_id)
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
    return owner


@router.post("/", response_model=Owner)
async def create_owner(owner: OwnerCreate, use_case: OwnerUseCase = Depends(get_owner_use_case)):
    """Crea un nuevo propietario."""
    return use_case.create_owner(owner.dict())


@router.put("/{owner_id}", response_model=Owner)
async def update_owner(
    owner_id: int, 
    owner: OwnerUpdate, 
    use_case: OwnerUseCase = Depends(get_owner_use_case)
):
    """Actualiza un propietario existente."""
    updated_owner = use_case.update_owner(owner_id, owner.dict())
    if not updated_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
    return updated_owner


@router.delete("/{owner_id}", response_model=dict)
async def delete_owner(owner_id: int, use_case: OwnerUseCase = Depends(get_owner_use_case)):
    """Elimina un propietario."""
    success = use_case.delete_owner(owner_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Propietario no encontrado")
    return {"message": "Propietario eliminado correctamente"}