"""Caso de uso: consultas m\u00e9dicas paginadas (BE-015-T05).

Depende de: BE-015-T01 (schemas Pydantic) y modelo Consultation.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import (
    ConsultationSummaryDto,
    PaginatedResponse,
)


def report_consultations(
    db: Session,
    clinic_id: int,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse[ConsultationSummaryDto]:
    """Devuelve consultas m\u00e9dicas filtradas por cl\u00ednica y rango de fechas.\n\n
    Args:\n        db: DB session (inyectada).\n        clinic_id: ID de la cl\u00ednica (tenant isolation).\n        period_start: Filtro por fecha inicio (opcional).\n        period_end: Filtro por fecha fin (opcional).\n        page: N\u00famero de p\u00e1gina (1-indexed).\n        size: Tama\u00f1o de p\u00e1gina.\n\n    Returns:\n        PaginatedResponse con lista de ConsultationSummaryDto.
    """
    from app.infrastructure.database.models.consultation import Consultation

    query = db.query(Consultation).filter(
        Consultation.clinic_id == clinic_id,
    )

    if period_start:
        query = query.filter(Consultation.updated_at >= period_start)
    if period_end:
        query = query.filter(Consultation.updated_at <= period_end)

    total = query.count()

    items = (
        query.order_by(Consultation.updated_at.desc(), Consultation.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    dto_items: list[ConsultationSummaryDto] = [
        ConsultationSummaryDto(
            id=item.id,
            clinic_id=item.clinic_id,
            pet_name=None,
            veterinarian_name=None,
            diagnosis=item.diagnosis,
            history=item.history,
            recommendations=item.recommendations,
        )
        for item in items
    ]

    return PaginatedResponse(
        items=dto_items,  # type: ignore[arg-type]
        total=total,
        page=page,
        size=size,
    )
