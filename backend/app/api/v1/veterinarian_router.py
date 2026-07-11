"""Router para veterinarios."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_veterinarian_use_case
from app.api.schemas.veterinarian_schema import VeterinarianResponse
from app.application.use_cases.veterinarian_use_case import VeterinarianUseCase
from app.domain.entities.veterinarian import VeterinarianCreate, VeterinarianUpdate

router = APIRouter(prefix="/veterinarians", tags=["veterinarians"])


@router.get("/", response_model=List[VeterinarianResponse])
async def get_veterinarians(
    branch_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    use_case: VeterinarianUseCase = Depends(get_veterinarian_use_case),
):
    """Obtiene una lista paginada de veterinarios para una sucursal."""
    return use_case.get_veterinarians(branch_id, skip, limit)


@router.get("/{veterinarian_id}", response_model=VeterinarianResponse)
async def get_veterinarian(
    veterinarian_id: int,
    use_case: VeterinarianUseCase = Depends(get_veterinarian_use_case),
):
    """Obtiene un veterinario por ID."""
    veterinarian = use_case.get_veterinarian(veterinarian_id)
    if not veterinarian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado",
        )
    return veterinarian


@router.post(
    "/",
    response_model=VeterinarianResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_veterinarian(
    veterinarian_data: VeterinarianCreate,
    use_case: VeterinarianUseCase = Depends(get_veterinarian_use_case),
):
    """Crea un nuevo veterinario."""
    return use_case.create_veterinarian(veterinarian_data)


@router.put("/{veterinarian_id}", response_model=VeterinarianResponse)
async def update_veterinarian(
    veterinarian_id: int,
    veterinarian_data: VeterinarianUpdate,
    use_case: VeterinarianUseCase = Depends(get_veterinarian_use_case),
):
    """Actualiza un veterinario existente."""
    updated = use_case.update_veterinarian(veterinarian_id, veterinarian_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado",
        )
    return updated


@router.delete("/{veterinarian_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_veterinarian(
    veterinarian_id: int,
    use_case: VeterinarianUseCase = Depends(get_veterinarian_use_case),
):
    """Elimina un veterinario."""
    success = use_case.delete_veterinarian(veterinarian_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veterinario no encontrado",
        )
