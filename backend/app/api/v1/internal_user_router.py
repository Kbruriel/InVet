"""
Router para usuarios internos - API v1
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases.internal_user_use_case import InternalUserUseCase
from app.api.dependencies import (
    get_internal_user_use_case_dep,
    require_owner_or_admin,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/internal-users", tags=["internal_users"])


@router.post("/", response_model="dict", status_code=status.HTTP_201_CREATED)
async def create_internal_user(
    user_data: "dict",
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Crea un nuevo usuario interno (solo admin o dueño de sucursal)"""
    try:
        use_case: InternalUserUseCase = get_internal_user_use_case_dep(current_user)
        # Validar ownership antes de crear
        if current_user["role"] != "admin":
            user_owner_branch_db = next(
                (u for u in current_user.get("branches", [])), None
            )
            if not user_owner_branch_db or user_data.get("branch_id") != user_owner_branch_db["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para crear usuarios en esta sucursal")
        return use_case.create_internal_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model="List[dict]")
async def get_internal_users(
    branch_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    use_case: InternalUserUseCase = Depends(get_internal_user_use_case_dep),
):
    """Obtiene una lista paginada de usuarios internos para una sucursal"""
    return use_case.get_internal_users(branch_id, skip, limit)


@router.get("/{user_id}", response_model="dict")
async def get_internal_user(
    user_id: int,
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Obtiene un usuario interno por ID con validación de ownership"""
    use_case: InternalUserUseCase = get_internal_user_use_case_dep(current_user)
    user = use_case.get_internal_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario interno no encontrado")
    # Validación IDOR/BOLA: verificar que el usuario pertenece al branch del usuario
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        if user.branch_id not in user_branches:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return user


@router.put("/{user_id}", response_model="dict")
async def update_internal_user(
    user_id: int,
    user_data: "dict",
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Actualiza un usuario interno con validación de ownership (IDOR/BOLA)"""
    use_case: InternalUserUseCase = get_internal_user_use_case_dep(current_user)
    existing = use_case.get_internal_user(user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario interno no encontrado")
    # Validación IDOR/BOLA
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        if existing.branch_id not in user_branches:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    updated = use_case.update_internal_user(user_id, user_data)
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_internal_user(
    user_id: int,
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Elimina un usuario interno con validación de ownership (IDOR/BOLA)"""
    use_case: InternalUserUseCase = get_internal_user_use_case_dep(current_user)
    existing = use_case.get_internal_user(user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario interno no encontrado")
    # Validación IDOR/BOLA - crítica para evitar BOLA
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        # Validar que el usuario es owner o editor de la sucursal a la que pertence este usuario
        user_owner_branch_db = next(
            (u for u in current_user.get("branches", [])), None
        )
        if not user_owner_branch_db or user_owner_branch_db["id"] != existing.branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    success = use_case.delete_internal_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar usuario interno")