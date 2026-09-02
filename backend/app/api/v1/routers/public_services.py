"""Router para listados públicos de servicios."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.v1.routers.public_query_params import (
    reject_unknown_query_params,
    resolve_public_page_size,
)
from app.api.v1.schemas.public_service import PublicServicesPaginatedResponse
from app.application.use_cases.public_services import ListPublicServicesUseCase
from app.core.database import get_db
from app.core.rate_limiter import public_rate_limiter
from app.infrastructure.database.repositories.branch_repository import (
    ServiceRepositoryImpl,
)

router = APIRouter(prefix="/servicios", tags=["public-services"])


def get_public_service_list_use_case(
    db: Session = Depends(get_db),
) -> ListPublicServicesUseCase:
    """Inyección de dependencias para el caso de uso de listados públicos."""
    service_repo = ServiceRepositoryImpl(db)
    return ListPublicServicesUseCase(service_repo)


@router.get("", response_model=PublicServicesPaginatedResponse)
async def list_servicios(
    request: Request,
    page: int = Query(1, ge=1, description="Número de página (comienza en 1)"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página (máximo 100)"),
    limit: int | None = Query(
        None, ge=1, le=100, description="Alias de tamaño de página"
    ),
    page_size: int | None = Query(
        None, ge=1, le=100, description="Alias de tamaño de página"
    ),
    sucursal_id: int | None = Query(None, description="Filtro por ID de sucursal"),
    clinica_id: int | None = Query(None, description="Filtro por ID de clínica"),
    search: str | None = Query(None, description="Filtro por nombre del servicio"),
    use_case: ListPublicServicesUseCase = Depends(get_public_service_list_use_case),
) -> PublicServicesPaginatedResponse:
    """Listar servicios públicos con filtros y paginación.

    Endpoint público — sin autenticación requerida.
    Rate limit: 60 requests per minute per IP (enforced by application middleware).

    ## CORS
    Los navegadores deben enviar credenciales si el frontend está en otro dominio.
    Configurar `Access-Control-Allow-Origin` con el origen del frontend en `main.py`.
    """
    reject_unknown_query_params(
        request,
        {
            "page",
            "size",
            "limit",
            "page_size",
            "sucursal_id",
            "clinica_id",
            "search",
        },
    )

    # Aplicar rate limiting
    await public_rate_limiter(request)

    try:
        effective_size = resolve_public_page_size(size, limit, page_size)
        result = await use_case.execute(
            page=page,
            size=effective_size,
            sucursal_id=sucursal_id,
            clinica_id=clinica_id,
            search=search,
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
            detail="Error interno al listar servicios",
        ) from exc
