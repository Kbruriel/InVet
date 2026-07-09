"""
Router para servicios - API v1
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.use_cases.service_use_case import ServiceUseCase
from app.api.dependencies import (
    get_service_use_case_dep,
    require_owner_or_admin,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/", response_model="dict", status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: "dict",
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Crea un nuevo servicio (solo admin o dueño de sucursal)"""
    try:
        use_case: ServiceUseCase = get_service_use_case_dep(current_user)
        # Validar ownership antes de crear
        if current_user["role"] != "admin":
            service_owner_branch_db = next(
                (u for u in current_user.get("branches", [])), None
            )
            if not service_owner_branch_db or service_data.get("branch_id") != service_owner_branch_db["id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permiso para crear servicios en esta sucursal")
        return use_case.create_service(service_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model="List[dict]")
async def get_services(
    branch_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    use_case: ServiceUseCase = Depends(get_service_use_case_dep),
):
    """Obtiene una lista paginada de servicios para una sucursal"""
    return use_case.get_services(branch_id, skip, limit)


@router.get("/{service_id}", response_model="dict")
async def get_service(
    service_id: int,
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Obtiene un servicio por ID con validación de ownership"""
    use_case: ServiceUseCase = get_service_use_case_dep(current_user)
    service = use_case.get_service(service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    # Validación IDOR/BOLA: verificar que el servicio pertenece al branch del usuario
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        # Corrected to check service.branch_id against user branches (not service_id)
        if service.branch_id not in user_branches:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    return service


@router.put("/{service_id}", response_model="dict")
async def update_service(
    service_id: int,
    service_data: "dict",
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Actualiza un servicio con validación de ownership (IDOR/BOLA)"""
    use_case: ServiceUseCase = get_service_use_case_dep(current_user)
    existing = use_case.get_service(service_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    # Validación IDOR/BOLA
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        if existing.branch_id not in user_branches:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    updated = use_case.update_service(service_id, service_data)
    return updated


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    current_user: "dict" = Depends(require_owner_or_admin),
):
    """Elimina un servicio con validación de ownership (IDOR/BOLA)"""
    use_case: ServiceUseCase = get_service_use_case_dep(current_user)
    existing = use_case.get_service(service_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    # Validación IDOR/BOLA - crítica para evitar BOLA
    if current_user["role"] != "admin":
        user_branches = [b.get("id") for b in current_user.get("branches", [])]
        # Validar que el usuario es owner o editor de la sucursal a la que pertence este servicio
        service_owner_branch_db = next(
            (u for u in current_user.get("branches", [])), None
        )
        if not service_owner_branch_db or service_owner_branch_db["id"] != existing.branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")
    success = use_case.delete_service(service_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar servicio")