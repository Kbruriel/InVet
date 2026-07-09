"""
Router para veterinarios - API v1
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases.veterinarian_use_case import VeterinarianUseCase
from app.api.dependencies import (
    get_veterinarian_use_case_dep,
    require_owner_or_admin,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/veterinarians", tags=["veterinarians"])


@router.post("/", response_model="dict", status_code=status.HTTP_201_CREATED)
async def create_veterinarian(
    veterinarian_data: "dict",
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Crea un nuevo veterinario (solo admin o dueño de sucursal)"""
    try:
        use_case: VeterinarianUseCase = get_veterinarian_use_case_dep(current_user)
        # Validar ownership antes de crear
        if current_user["role"] != "admin":
            veterinarian_owner_branch_db = next(
                (u for u in current_user.get("branches", [])), None
            )
            if not veterinarian_owner_branch_db or veterinarian_data.get("branch_id") != veterinarian_owner_branch_db["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para crear veterinarios en esta sucursal")
        return use_case.create_veterinarian(veterinarian_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model="List[dict]")
async def get_veterinarians(
    branch_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    use_case: VeterinarianUseCase = Depends(get_veterinarian_use_case_dep),
):
    """Obtiene una lista paginada de veterinarios para una sucursal"""
    return use_case.get_veterinarians(branch_id, skip, limit)


@router.get("/{veterinarian_id}", response_model="dict")
async def get_veterinarian(
    veterinarian_id: int,
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Obtiene un veterinario por ID con validación de ownership"""
    use_case: VeterinarianUseCase = get_veterinarian_use_case_dep(current_user)
    veterinarian = use_case.get_veterinarian(veterinarian_id)
    if not veterinarian:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinario no encontrado")
    # Validación IDOR/BOLA: verificar que el usuario pertenece al branch del veterinario
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        if veterinarian.branch_id not in user_branches:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return veterinarian


@router.put("/{veterinarian_id}", response_model="dict")
async def update_veterinarian(
    veterinarian_id: int,
    veterinarian_data: "dict",
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Actualiza un veterinario con validación de ownership (IDOR/BOLA)"""
    use_case: VeterinarianUseCase = get_veterinarian_use_case_dep(current_user)
    existing = use_case.get_veterinarian(veterinarian_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinario no encontrado")
    # Validación IDOR/BOLA
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        if existing.branch_id not in user_branches:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    updated = use_case.update_veterinarian(veterinarian_id, veterinarian_data)
    return updated


@router.delete("/{veterinarian_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_veterinarian(
    veterinarian_id: int,
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Elimina un veterinario con validación de ownership (IDOR/BOLA)"""
    use_case: VeterinarianUseCase = get_veterinarian_use_case_dep(current_user)
    existing = use_case.get_veterinarian(veterinarian_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veterinario no encontrado")
    # Validación IDOR/BOLA - crítica para evitar BOLA
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        # Validar que el usuario es owner o editor de la sucursal a la que pertence este veterinario
        veterinarian_owner_branch_db = next(
            (u for u in current_user.get("branches", [])), None
        )
        if not veterinarian_owner_branch_db or veterinarian_owner_branch_db["id"] != existing.branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    success = use_case.delete_veterinarian(veterinarian_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar veterinario")