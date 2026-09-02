"""Router FastAPI para reseñas y respuestas clínicas (BE-012-T05).

Expone los endpoints de reseñas sin lógica de negocio: los casos de uso en
``app.application.use_cases.review`` encapsulan las reglas, y el router solo
mapea las excepciones de dominio a estados HTTP (401/403/404/409/422).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.review_schemas import (
    ReviewCreate,
    ReviewList,
    ReviewListMeta,
    ReviewRead,
    ReviewRespond,
    ReviewResponseRead,
)
from app.application.use_cases.review import (
    ReviewError,
    ReviewService,
)
from app.core.security import get_current_access_user
from app.data.review_repo import ReviewRepository
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.branch_repository import (
    BranchRepository,
    RatingSummaryRepository,
)
from app.infrastructure.database.repositories.appointment_repository_impl import (
    AppointmentRepositoryImpl,
)
from app.infrastructure.database.repositories.branch_repository import (
    BranchRepositoryImpl,
    RatingSummaryRepositoryImpl,
)
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/reviews", tags=["reviews"])

# Roles clínicos que pueden responder una reseña (rol propietario/client bloqueado).
_RESPOND_ROLES = {"veterinarian", "clinic", "staff", "admin", "internal"}
# Roles clínicos que pueden consultar el listado de reseñas de su clínica.
_CLINIC_ROLES = _RESPOND_ROLES


def get_review_repo(db: Session = Depends(get_db)) -> ReviewRepository:
    """Repositorio de reseñas (ABC + impl. SQLAlchemy)."""
    from app.data.review_repo import ReviewRepositoryImpl

    return ReviewRepositoryImpl(db)


def get_appointment_repo(db: Session = Depends(get_db)) -> AppointmentRepository:
    """Repositorio de citas (validación de COMPLETED + tenant)."""
    return AppointmentRepositoryImpl(db)


def get_rating_repo(db: Session = Depends(get_db)) -> RatingSummaryRepository:
    """Repositorio de resumen de calificaciones (recalcular al crear reseña)."""
    return RatingSummaryRepositoryImpl(db)


def get_review_service(
    review_repo: ReviewRepository = Depends(get_review_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    rating_repo: RatingSummaryRepository = Depends(get_rating_repo),
) -> ReviewService:
    """Fachada de casos de uso de reseñas (BE-012-T04)."""
    return ReviewService(review_repo, appointment_repo, rating_repo)


# ---------------------------------------------------------------------------
# Helpers de tenant / rol
# ---------------------------------------------------------------------------
def _get_clinic_id_from_user(current_user: dict) -> int:
    clinic_id = current_user.get("clinic_id") or current_user.get("tenant_id")
    if clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una clínica asociada.",
        )
    return int(clinic_id)


def _get_user_id_from_user(current_user: dict) -> int:
    user_id = current_user.get("user_id") or current_user.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado.",
        )
    return int(user_id)


def _require_respond_role(current_user: dict) -> None:
    role = current_user.get("role")
    if role not in _RESPOND_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el equipo clínico de la sucursal puede responder reseñas.",
        )


def _require_clinic_role(current_user: dict) -> None:
    role = current_user.get("role")
    if role not in _CLINIC_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo personal asignado a la clínica puede listar reseñas.",
        )


def get_branch_repo(db: Session = Depends(get_db)) -> BranchRepository:
    """Repositorio de sucursales (validación 404 en el listado público)."""
    return BranchRepositoryImpl(db)


# ---------------------------------------------------------------------------
# POST /reviews — crear reseña (rol propietario/client)
# ---------------------------------------------------------------------------
@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    current_user: dict = Depends(get_current_access_user),
    service: ReviewService = Depends(get_review_service),
) -> ReviewRead:
    """Calificar una cita COMPLETED (una reseña única por cita).

    - Solo el propietario/client titular de la cita puede calificar (403).
    - La cita debe existir en la clínica del usuario y estar COMPLETED (422).
    - Una cita ya calificada no admite segunda reseña (409).
    """
    try:
        result = await service.create(payload, current_user)
    except ReviewError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
    return ReviewRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /reviews/public/{branch_id} — listado público paginado (anónimo)
# ---------------------------------------------------------------------------
@router.get(
    "/public/{branch_id}",
    response_model=ReviewList,
)
async def list_public_reviews(
    branch_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
    branch_repo: BranchRepository = Depends(get_branch_repo),
) -> ReviewList:
    """Listado público paginado de reseñas de una sucursal (sin autenticación).

    Sucursal inexistente o no publicada devuelve 404. Meta con
    ``page``, ``page_size``, ``total``, ``pages``.
    """
    branch = await branch_repo.get_branch_by_id(branch_id)
    if branch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sucursal no encontrada"
        )
    items, total = await service.list_public(
        branch_id=branch_id, page=page, page_size=page_size
    )
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ReviewList(
        items=[ReviewRead.model_validate(i) for i in items],
        meta=ReviewListMeta(page=page, page_size=page_size, total=total, pages=pages),
    )


# ---------------------------------------------------------------------------
# GET /reviews — listado clínico paginado (tenant isolation)
# ---------------------------------------------------------------------------
@router.get("", response_model=ReviewList)
async def list_clinic_reviews(
    branch_id: int | None = Query(None, gt=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_access_user),
    service: ReviewService = Depends(get_review_service),
) -> ReviewList:
    """Listado clínico paginado de reseñas de la clínica del usuario.

    Solo personal asignado a la clínica puede listar (403 para propietario).
    Siempre filtrado por ``clinic_id`` del token (BOLA).
    """
    _require_clinic_role(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)
    items, total = await service.list_clinical(
        clinic_id=clinic_id,
        branch_id=branch_id,
        page=page,
        page_size=page_size,
    )
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ReviewList(
        items=[ReviewRead.model_validate(i) for i in items],
        meta=ReviewListMeta(page=page, page_size=page_size, total=total, pages=pages),
    )


# ---------------------------------------------------------------------------
# GET /reviews/{review_id} — detalle autenticado (propietario o tenant clínico)
# ---------------------------------------------------------------------------
@router.get("/{review_id}", response_model=ReviewRead)
async def get_review(
    review_id: int,
    current_user: dict = Depends(get_current_access_user),
    service: ReviewService = Depends(get_review_service),
) -> ReviewRead:
    """Obtener detalle de una reseña con aislamiento de tenant.

    - Propietario de la reseña (owner/client) o personal clínico del tenant.
    - Reseña de otra clínica → 404 (BOLA consistente).
    - Sin token → 401.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    try:
        result = await service.get(review_id, clinic_id)
    except ReviewError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
    return ReviewRead.model_validate(result)


# ---------------------------------------------------------------------------
# POST /reviews/{review_id}/respond — responder una reseña (rol clínico)
# ---------------------------------------------------------------------------
@router.post("/{review_id}/respond", response_model=ReviewResponseRead)
async def respond_review(
    review_id: int,
    payload: ReviewRespond,
    current_user: dict = Depends(get_current_access_user),
    service: ReviewService = Depends(get_review_service),
) -> ReviewResponseRead:
    """Responder una reseña (una única respuesta por reseña).

    - Solo roles clínicos de la sucursal pueden responder (403 propietario).
    - Reseña de otra sucursal/tenant → 404 (BOLA).
    - Una reseña ya respondida → 409.
    """
    _require_respond_role(current_user)
    try:
        review = await service.respond(review_id, payload, current_user)
    except ReviewError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
    if review.response is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Respuesta no disponible tras responder.",
        )
    return ReviewResponseRead.model_validate(review.response)
