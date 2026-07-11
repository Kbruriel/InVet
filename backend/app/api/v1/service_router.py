"""Router para servicios."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_service_use_case
from app.api.schemas.service_schema import ServiceResponse
from app.application.use_cases.service_use_case import ServiceUseCase
from app.domain.entities.service import ServiceCreate, ServiceUpdate

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=List[ServiceResponse])
async def get_services(
    branch_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    use_case: ServiceUseCase = Depends(get_service_use_case),
):
    """Obtiene una lista paginada de servicios para una sucursal."""
    return use_case.get_services(branch_id, skip, limit)


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    use_case: ServiceUseCase = Depends(get_service_use_case),
):
    """Obtiene un servicio por ID."""
    service = use_case.get_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )
    return service


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    use_case: ServiceUseCase = Depends(get_service_use_case),
):
    """Crea un nuevo servicio."""
    return use_case.create_service(service_data)


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    use_case: ServiceUseCase = Depends(get_service_use_case),
):
    """Actualiza un servicio existente."""
    updated = use_case.update_service(service_id, service_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )
    return updated


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    use_case: ServiceUseCase = Depends(get_service_use_case),
):
    """Elimina un servicio."""
    success = use_case.delete_service(service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )
