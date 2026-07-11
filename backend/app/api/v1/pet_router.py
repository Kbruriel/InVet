"""Router para mascotas."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.pet_schema import Pet, PetCreate, PetUpdate
from app.application.use_cases.pet_use_case import PetUseCase
from app.core.database import get_db
from app.domain.repositories.pet_repository import PetRepository
from app.infrastructure.database.repositories.pet_repository_impl import (
    PetRepositoryImpl,
)

router = APIRouter(prefix="/pets", tags=["pets"])


def get_pet_repository(db: Session = Depends(get_db)) -> PetRepository:
    """Inyección de dependencia para el repositorio de mascotas."""
    return PetRepositoryImpl(db)


def get_pet_use_case(
    repository: PetRepository = Depends(get_pet_repository),
) -> PetUseCase:
    """Inyección de dependencia para el caso de uso de mascotas."""
    return PetUseCase(repository)


@router.get("/", response_model=List[Pet])
async def get_pets(
    skip: int = 0, limit: int = 100, use_case: PetUseCase = Depends(get_pet_use_case)
):
    """Obtiene una lista paginada de mascotas."""
    return use_case.get_pets(skip=skip, limit=limit)


@router.get("/{pet_id}", response_model=Pet)
async def get_pet(pet_id: int, use_case: PetUseCase = Depends(get_pet_use_case)):
    """Obtiene una mascota por ID."""
    pet = use_case.get_pet(pet_id)
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    return pet


@router.post("/", response_model=Pet)
async def create_pet(pet: PetCreate, use_case: PetUseCase = Depends(get_pet_use_case)):
    """Crea una nueva mascota."""
    return use_case.create_pet(pet.dict())


@router.put("/{pet_id}", response_model=Pet)
async def update_pet(
    pet_id: int, pet: PetUpdate, use_case: PetUseCase = Depends(get_pet_use_case)
):
    """Actualiza una mascota existente."""
    updated_pet = use_case.update_pet(pet_id, pet.dict())
    if not updated_pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    return updated_pet


@router.delete("/{pet_id}", response_model=dict)
async def delete_pet(pet_id: int, use_case: PetUseCase = Depends(get_pet_use_case)):
    """Elimina una mascota."""
    success = use_case.delete_pet(pet_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mascota no encontrada"
        )
    return {"message": "Mascota eliminada correctamente"}
