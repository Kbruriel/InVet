"""Router para búsquedas de clínicas."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.clinic_search import ClinicSearchResponse
from app.application.use_cases.clinic_search import SearchClinicsUseCase
from app.core.database import get_db
from app.infrastructure.database.repositories.clinic_repository_impl import (
    ClinicRepositoryImpl,
)

router = APIRouter(prefix="/clinicas", tags=["search"])


def get_clinic_search_use_case(
    db: Session = Depends(get_db),
) -> SearchClinicsUseCase:
    """Inyección de dependencias para el caso de uso de búsqueda de clínicas."""
    clinic_repo = ClinicRepositoryImpl(db)
    return SearchClinicsUseCase(clinic_repo)


@router.get("/buscar", response_model=ClinicSearchResponse)
async def search_clinicas(
    location: str | None = Query(None, description="Ubicación para filtrar clínicas"),
    service_type: str | None = Query(
        None, description="Tipo de servicio para filtrar clínicas"
    ),
    page: int = Query(1, ge=1, description="Número de página (comienza en 1)"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página (máximo 100)"),
    use_case: SearchClinicsUseCase = Depends(get_clinic_search_use_case),
) -> ClinicSearchResponse:
    """Buscar clínicas públicas por ubicación o tipo de servicio.

    Solo se devuelven clínicas activas y visibles públicamente.
    """
    try:
        clinics = await use_case.execute(
            location=location,
            service_type=service_type,
            page=page,
            size=size,
        )

        return clinics
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al buscar clínicas",
        ) from exc
