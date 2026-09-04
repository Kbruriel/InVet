"""Router FastAPI para reportes operativos (BE-015-T08).

Endpoints: /reports/{appointments,services,pets,consultations,ratings,payments}.
Todos los endpoints dependen de get_current_access_user para tenant isolation con Jet.
"""

from collections.abc import Generator
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import (
    AppointmentSummaryDto,
    ConsultationSummaryDto,
    PaginatedResponse,
    PetCountDto,
    ServiceSummaryDto,
)
from app.application.usecases.reports.report_appointments import (
    report_appointments as uc_appointments,
)
from app.application.usecases.reports.report_consultations import (
    report_consultations as uc_consultations,
)
from app.application.usecases.reports.report_payments import (
    report_payments as uc_payments,
)
from app.application.usecases.reports.report_pets_count import (
    report_pets_count as uc_pets,
)
from app.application.usecases.reports.report_ratings_summary import (
    report_ratings_summary as uc_ratings,
)
from app.application.usecases.reports.report_services import (
    report_services as uc_services,
)
from app.core.security import get_current_access_user

router = APIRouter(tags=["reports"])


# ---------------------------------------------------------------------------
# Respuestas personalizadas que no tienen model Pydantic en report_schemas.py
# ---------------------------------------------------------------------------


class RatingsReportResponse(BaseModel):
    by_veterinarian: list[dict[str, Any]] = Field(
        description="Lista de ratings agrupados por veterinario."
    )
    clinic_avg: float = Field(
        description="Promedio de calificaciones de toda la clinica."
    )


class PaymentsReportResponse(BaseModel):
    items: list[dict[str, Any]] = Field(description="Pagos paginados.")
    total: int = Field(description="Total de pagos encontrados.")
    page: int = Field(description="Pagina actual.")
    size: int = Field(description="Elementos por pagina.")
    total_amount: float = Field(
        description="Suma del monto total de los pagos en esta pagina."
    )


# ---------------------------------------------------------------------------
# Helpers internos (router only -- zero business logic)
# ---------------------------------------------------------------------------


def _db() -> Generator[Session, None, None]:
    from app.infrastructure.database.session import get_db as _inner

    yield from _inner()


def _clinic_id_from(current_user: dict) -> int:
    cid = current_user.get("clinic_id") or current_user.get("tenant_id")
    if cid is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una clinica asociada.",
        )
    return int(cid)


def _validate_dates(ps: str | None, pe: str | None) -> tuple[datetime | None, datetime | None]:
    start: datetime | None = None
    end: datetime | None = None

    if ps:
        try:
            start = datetime.strptime(ps, "%Y-%m-%d")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="period_start debe estar en formato YYYY-MM-DD.",
            ) from exc

    if pe:
        try:
            end = datetime.strptime(pe, "%Y-%m-%d")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="period_end debe estar en formato YYYY-MM-DD.",
            ) from exc

    if start and end and start > end:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="period_end no puede ser anterior a period_start.",
        )

    return start, end


# ---------------------------------------------------------------------------
# GET /reports/appointments
# ---------------------------------------------------------------------------


@router.get(
    "/appointments",
    response_model=PaginatedResponse[AppointmentSummaryDto],
    summary="Reporte paginado de citas medicas",
)
def get_appointments_report(
    period_start: str | None = Query(None),
    period_end: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_access_user),
    db: Session = Depends(_db),
) -> PaginatedResponse[AppointmentSummaryDto]:
    start, end = _validate_dates(period_start, period_end)
    return uc_appointments(  # type: ignore
        db=db,
        clinic_id=_clinic_id_from(current_user),
        period_start=start,
        period_end=end,
        page=page,
        size=size,
    )


# ---------------------------------------------------------------------------
# GET /reports/services
# ---------------------------------------------------------------------------

@router.get(
    "/services",
    response_model=PaginatedResponse[ServiceSummaryDto],
    summary="Reporte paginado de servicios",
)
def get_services_report(
    period_start: str | None = Query(None),
    period_end: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_access_user),
    db: Session = Depends(_db),
) -> PaginatedResponse[ServiceSummaryDto]:
    start, end = _validate_dates(period_start, period_end)
    return uc_services(  # type: ignore
        db=db,
        clinic_id=_clinic_id_from(current_user),
        period_start=start,
        period_end=end,
        page=page,
        size=size,
    )


# ---------------------------------------------------------------------------
# GET /reports/pets
# ---------------------------------------------------------------------------

@router.get(
    "/pets",
    response_model=PetCountDto,
    summary="Conteo de mascotas activas por clinica",
)
def get_pets_report(
    period_start: str | None = Query(None),
    period_end: str | None = Query(None),
    current_user: dict = Depends(get_current_access_user),
    db: Session = Depends(_db),
) -> PetCountDto:
    start, end = _validate_dates(period_start, period_end)
    result = uc_pets(  # type: ignore
        db=db,
        clinic_id=_clinic_id_from(current_user),
        period_start=start,
        period_end=end,
    )
    return result.items[0]  # type: ignore


# ---------------------------------------------------------------------------
# GET /reports/consultations
# ---------------------------------------------------------------------------

@router.get(
    "/consultations",
    response_model=PaginatedResponse[ConsultationSummaryDto],
    summary="Reporte paginado de consultas medicas",
)
def get_consultations_report(
    period_start: str | None = Query(None),
    period_end: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_access_user),
    db: Session = Depends(_db),
) -> PaginatedResponse[ConsultationSummaryDto]:
    start, end = _validate_dates(period_start, period_end)
    return uc_consultations(  # type: ignore
        db=db,
        clinic_id=_clinic_id_from(current_user),
        period_start=start,
        period_end=end,
        page=page,
        size=size,
    )


# ---------------------------------------------------------------------------
# GET /reports/ratings
# ---------------------------------------------------------------------------

@router.get(
    "/ratings",
    response_model=RatingsReportResponse,
    summary="Resumen de calificaciones por veterinario y clinica",
)
def get_ratings_report(
    period_start: str | None = Query(None),
    period_end: str | None = Query(None),
    current_user: dict = Depends(get_current_access_user),
    db: Session = Depends(_db),
) -> RatingsReportResponse:
    start, end = _validate_dates(period_start, period_end)
    result = uc_ratings(  # type: ignore
        db=db,
        clinic_id=_clinic_id_from(current_user),
        period_start=start,
        period_end=end,
    )

    by_vet: list[dict] = []
    ratings_vals: list[float] = []

    for item in result.items:  # type: ignore[attr-defined]
        avg = item.average_rating  # type: ignore[attr-defined]
        ratings_vals.append(avg)
        by_vet.append(
            {
                "vet_id": item.veterinarian_id,
                "average_rating": avg,
                "total_reviews": item.total_reviews,  # type: ignore[attr-defined]
            }
        )

    clinic_avg = sum(ratings_vals) / len(ratings_vals) if ratings_vals else 0.0

    return RatingsReportResponse(
        by_veterinarian=by_vet,
        clinic_avg=round(clinic_avg, 2),
    )


# ---------------------------------------------------------------------------
# GET /reports/payments
# ---------------------------------------------------------------------------

@router.get(
    "/payments",
    response_model=PaymentsReportResponse,
    summary="Reporte paginado de pagos operativos",
)
def get_payments_report(
    period_start: str | None = Query(None),
    period_end: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_access_user),
    db: Session = Depends(_db),
) -> PaymentsReportResponse:
    start, end = _validate_dates(period_start, period_end)
    result = uc_payments(  # type: ignore
        db=db,
        clinic_id=_clinic_id_from(current_user),
        period_start=start,
        period_end=end,
        page=page,
        size=size,
    )

    total_amount = sum((i.amount for i in result.items), 0)  # type: ignore[attr-defined]

    return PaymentsReportResponse(
        items=[i.model_dump() for i in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
        total_amount=round(total_amount, 2),
    )
