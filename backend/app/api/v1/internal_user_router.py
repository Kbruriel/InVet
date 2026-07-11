"""Router para usuarios internos."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_internal_user_use_case
from app.api.schemas.internal_user_schema import InternalUserResponse
from app.application.use_cases.internal_user_use_case import InternalUserUseCase
from app.domain.entities.internal_user import InternalUserCreate, InternalUserUpdate

router = APIRouter(prefix="/internal-users", tags=["internal_users"])


@router.get("/", response_model=List[InternalUserResponse])
async def get_internal_users(
    branch_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    use_case: InternalUserUseCase = Depends(get_internal_user_use_case),
):
    """Obtiene una lista paginada de usuarios internos para una sucursal."""
    return use_case.get_internal_users(branch_id, skip, limit)


@router.get("/{user_id}", response_model=InternalUserResponse)
async def get_internal_user(
    user_id: int,
    use_case: InternalUserUseCase = Depends(get_internal_user_use_case),
):
    """Obtiene un usuario interno por ID."""
    user = use_case.get_internal_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado",
        )
    return user


@router.post(
    "/",
    response_model=InternalUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_internal_user(
    user_data: InternalUserCreate,
    use_case: InternalUserUseCase = Depends(get_internal_user_use_case),
):
    """Crea un nuevo usuario interno."""
    return use_case.create_internal_user(user_data)


@router.put("/{user_id}", response_model=InternalUserResponse)
async def update_internal_user(
    user_id: int,
    user_data: InternalUserUpdate,
    use_case: InternalUserUseCase = Depends(get_internal_user_use_case),
):
    """Actualiza un usuario interno existente."""
    updated = use_case.update_internal_user(user_id, user_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado",
        )
    return updated


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_internal_user(
    user_id: int,
    use_case: InternalUserUseCase = Depends(get_internal_user_use_case),
):
    """Elimina un usuario interno."""
    success = use_case.delete_internal_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario interno no encontrado",
        )
