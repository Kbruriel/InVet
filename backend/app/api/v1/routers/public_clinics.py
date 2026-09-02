"""Router para listados públicos de clínicas."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.v1.routers.public_query_params import (
    reject_unknown_query_params,
    resolve_public_page_size,
)
from app.api.v1.schemas.public_clinic import (
    PublicClinicDetailDTO,
    PublicClinicsPaginatedResponse,
)
from app.application.use_cases.public_clinics import ListPublicClinicsUseCase
from app.core.database import get_db
from app.core.rate_limiter import public_rate_limiter
from app.infrastructure.database.repositories.clinic_repository_impl import (
    ClinicRepositoryImpl,
)

router = APIRouter(prefix="/clinicas", tags=["public-clinics"])


def get_public_clinic_list_use_case(
    db: Session = Depends(get_db),
) -> ListPublicClinicsUseCase:
    """Inyección de dependencias para el caso de uso de listados públicos."""
    clinic_repo = ClinicRepositoryImpl(db)
    return ListPublicClinicsUseCase(clinic_repo)


@router.get("", response_model=PublicClinicsPaginatedResponse)
async def list_clinicas(
    request: Request,
    page: int = Query(1, ge=1, description="Número de página (comienza en 1)"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página (máximo 100)"),
    limit: int | None = Query(
        None, ge=1, le=100, description="Alias de tamaño de página"
    ),
    page_size: int | None = Query(
        None, ge=1, le=100, description="Alias de tamaño de página"
    ),
    search: str | None = Query(None, description="Filtro por nombre o ciudad"),
    service_type: str | None = Query(None, description="Filtro por tipo de servicio"),
    use_case: ListPublicClinicsUseCase = Depends(get_public_clinic_list_use_case),
) -> PublicClinicsPaginatedResponse:
    """Listar clínicas públicas con paginación.

    Endpoint público — sin autenticación requerida.
    Rate limit: 60 requests per minute per IP (enforced by application middleware).

    ## CORS
    Los navegadores deben enviar credenciales si el frontend está en otro dominio.
    Configurar `Access-Control-Allow-Origin` con el origen del frontend en `main.py`.
    """
    reject_unknown_query_params(
        request,
        {"page", "size", "limit", "page_size", "search", "service_type"},
    )

    # Aplicar rate limiting
    await public_rate_limiter(request)

    try:
        effective_size = resolve_public_page_size(size, limit, page_size)
        result = await use_case.execute(
            page=page,
            size=effective_size,
            search=search,
            service_type=service_type,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parámetro inválido: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al listar clínicas",
        ) from exc


@router.get("/{clinic_id}", response_model=PublicClinicDetailDTO)
async def get_clinica(
    request: Request,
    clinic_id: int,
    use_case: ListPublicClinicsUseCase = Depends(get_public_clinic_list_use_case),
) -> PublicClinicDetailDTO:
    """Detalle de una clínica pública.

    Endpoint público — sin autenticación requerida.
    Rate limit: 60 requests per minute per IP (enforced by application middleware).

    ## CORS
    Los navegadores deben enviar credenciales si el frontend está en otro dominio.
    Configurar `Access-Control-Allow-Origin` con el origen del frontend en `main.py`.
    """
    # Aplicar rate limiting
    await public_rate_limiter(request)

    try:
        result = await use_case.get_by_id(clinic_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clínica no encontrada",
            )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener el detalle de la clínica",
        ) from exc
