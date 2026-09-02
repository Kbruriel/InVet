"""Router para listados públicos de sucursales."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.v1.routers.public_query_params import (
    reject_unknown_query_params,
    resolve_public_page_size,
)
from app.api.v1.schemas.public_branch import PublicBranchesPaginatedResponse
from app.application.use_cases.public_branches import ListPublicBranchesUseCase
from app.core.database import get_db
from app.domain.repositories.branch_repository import BranchRepository

router = APIRouter(prefix="/sucursales", tags=["public-branches"])


def get_public_branch_list_use_case(
    db: Session = Depends(get_db),
) -> ListPublicBranchesUseCase:
    """Inyección de dependencias para el caso de uso de listados públicos."""
    from app.infrastructure.database.repositories.branch_repository import (
        BranchRepositoryImpl,
    )

    branch_repo: BranchRepository = BranchRepositoryImpl(db)
    return ListPublicBranchesUseCase(branch_repo)


@router.get("", response_model=PublicBranchesPaginatedResponse)
async def list_sucursales(
    request: Request,
    page: int = Query(1, ge=1, description="Número de página (comienza en 1)"),
    size: int = Query(20, ge=1, le=100, description="Tamaño de página (máximo 100)"),
    limit: int | None = Query(
        None, ge=1, le=100, description="Alias de tamaño de página"
    ),
    page_size: int | None = Query(
        None, ge=1, le=100, description="Alias de tamaño de página"
    ),
    clinica_id: int | None = Query(None, description="Filtro por ID de clínica"),
    search: str | None = Query(None, description="Filtro por nombre o ciudad"),
    use_case: ListPublicBranchesUseCase = Depends(get_public_branch_list_use_case),
) -> PublicBranchesPaginatedResponse:
    """Listar sucursales públicas con filtros y paginación.

    Endpoint público — sin autenticación requerida.
    Rate limit: 60 requests per minute per IP (enforced by application middleware).

    ## CORS
    Los navegadores deben enviar credenciales si el frontend está en otro dominio.
    Configurar `Access-Control-Allow-Origin` con el origen del frontend en `main.py`.
    """
    reject_unknown_query_params(
        request,
        {"page", "size", "limit", "page_size", "clinica_id", "search"},
    )

    try:
        effective_size = resolve_public_page_size(size, limit, page_size)
        result = await use_case.execute(
            page=page,
            size=effective_size,
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
            detail="Error interno al listar sucursales",
        ) from exc
