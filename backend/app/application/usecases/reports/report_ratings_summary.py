"""Caso de uso: resumen de ratings por veterinario (BE-015-T06).

Depende de: BE-015-T01 (schemas Pydantic) y modelos RatingSummary/Branch.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import (
    PaginatedResponse,
    RatingSummaryDto,
)


def report_ratings_summary(
    db: Session,
    clinic_id: int,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse[RatingSummaryDto]:
    """Devuelve resumen de ratings filtrados por cl\u00ednica y rango de fechas.\n\n
    Args:\n        db: DB session (inyectada).\n        clinic_id: ID de la cl\u00ednica (tenant isolation).\n        period_start: Filtro por fecha inicio (opcional).\n        period_end: Filtro por fecha fin (opcional).\n        page: N\u00famero de p\u00e1gina (1-indexed).\n        size: Tama\u00f1o de p\u00e1gina.\n\n    Returns:\n        PaginatedResponse con lista de RatingSummaryDto.
    """
    from app.infrastructure.database.models.branch import Branch
    from app.infrastructure.database.models.rating_summary import RatingSummary

    query = (
        db.query(RatingSummary, Branch)
        .join(Branch, RatingSummary.branch_id == Branch.id)
        .filter(Branch.clinic_id == clinic_id)
    )

    if period_start:
        query = query.filter(RatingSummary.updated_at >= period_start)
    if period_end:
        query = query.filter(RatingSummary.updated_at <= period_end)

    total = query.count()

    items = (
        query.order_by(RatingSummary.created_at.desc(), RatingSummary.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    dto_items: list[RatingSummaryDto] = [
        RatingSummaryDto(
            veterinarian_id=None,  # no vet association in this model
            average_rating=rs.average_rating if rs.average_rating else 0.0,
            total_reviews=rs.total_reviews if rs.total_reviews else 0,
        )
        for rs, _branch in items
    ]

    return PaginatedResponse(
        items=dto_items,  # type: ignore[arg-type]
        total=total,
        page=page,
        size=size,
    )
