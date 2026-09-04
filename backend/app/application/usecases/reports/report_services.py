"""Caso de uso: reporte paginado de servicios por periodo (BE-015-T03).

Depende de: BE-015-T01 (schemas Pydantic) y modelo Service (BE-006).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import (
    PaginatedResponse,
    ServiceSummaryDto,
)


def report_services(
    db: Session,
    clinic_id: int,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse[ServiceSummaryDto]:
    """Devuelve servicios filtrados por clínica y rango de fechas de creación.

    Args:
        db: DB session (inyectada).
        clinic_id: ID de la clínica (tenant isolation).
        period_start: Filtro por fecha de creación (opcional).
        period_end: Filtro por fecha de creación (opcional).
        page: Número de página (1-indexed).
        size: Tamaño de página.

    Returns:
        PaginatedResponse con lista de ServiceSummaryDto.
    """
    from app.infrastructure.database.models.service_model import Service

    query = db.query(Service).filter(Service.clinic_id == clinic_id)

    if period_start:
        query = query.filter(Service.created_at >= period_start)
    if period_end:
        query = query.filter(Service.created_at <= period_end)

    total = query.count()

    items = (
        query.order_by(Service.name.asc(), Service.id.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    dto_items: list[ServiceSummaryDto] = [
        ServiceSummaryDto(
            id=s.id,
            clinic_id=s.clinic_id,
            name=s.name,
            description=s.description,
            price=(s.price / 100.0) if s.price is not None else 0.0,
            duration_minutes=s.duration_minutes,
            is_active=bool(s.is_active),
        )
        for s in items
    ]

    return PaginatedResponse(
        items=dto_items,
        total=total,
        page=page,
        size=size,
    )
