"""Caso de uso: pagos paginados (BE-015-T07).

Depende de: BE-015-T01 (schemas Pydantic) y modelo Payment.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import (
    PaginatedResponse,
    PaymentSummaryDto,
)


def report_payments(
    db: Session,
    clinic_id: int,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse[PaymentSummaryDto]:
    """Devuelve pagos filtrados por cl\u00ednica y rango de fechas.\n\n
    Args:\n        db: DB session (inyectada).\n        clinic_id: ID de la cl\u00ednica (tenant isolation).\n        period_start: Filtro por fecha inicio (opcional).\n        period_end: Filtro por fecha fin (opcional).\n        page: N\u00famero de p\u00e1gina (1-indexed).\n        size: Tama\u00f1o de p\u00e1gina.\n\n    Returns:\n        PaginatedResponse con lista de PaymentSummaryDto.
    """
    from app.infrastructure.database.models.payment import Payment

    query = db.query(Payment).filter(
        Payment.clinic_id == clinic_id,
    )

    if period_start:
        query = query.filter(Payment.paid_at >= period_start)
    if period_end:
        query = query.filter(Payment.paid_at <= period_end)

    total = query.count()

    items = (
        query.order_by(Payment.paid_at.desc(), Payment.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    dto_items: list[PaymentSummaryDto] = [
        PaymentSummaryDto(
            id=p.id,
            clinic_id=p.clinic_id,
            appointment_id=p.appointment_id,
            service_id=p.service_id,
            amount=p.amount / 100.0,  # stored as cents/int -> convert to float dollars
            payment_method=p.method.value,
            status=p.status.value,
            paid_at=p.paid_at.isoformat(),
        )
        for p in items
    ]

    return PaginatedResponse(
        items=dto_items,  # type: ignore[arg-type]
        total=total,
        page=page,
        size=size,
    )
