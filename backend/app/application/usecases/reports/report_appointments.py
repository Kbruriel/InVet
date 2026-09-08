"""Caso de uso: reporte paginado de citas m\u00e9dicas (BE-015-T02).

Depende de: BE-015-T01 (schemas Pydantic) y modelo Appointment (BE-008).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import (
    AppointmentSummaryDto,
    PaginatedResponse,
)


def report_appointments(
    db: Session,
    clinic_id: int,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    page: int = 1,
    size: int = 20,
) -> PaginatedResponse[AppointmentSummaryDto]:
    """Devuelve citas filtradas por c\u00ednica y rango de fechas.\n\n
    Args:\n        db: DB session (inyectada).\n        clinic_id: ID de la cl\u00ednica (tenant isolation).\n        period_start: Filtro por fecha inicio (opcional).\n        period_end: Filtro por fecha fin (opcional).\n        page: N\u00famero de p\u00e1gina (1-indexed).\n        size: Tama\u00f1o de p\u00e1gina.\n\n    Returns:\n        PaginatedResponse con lista de AppointmentSummaryDto.
    """
    from app.infrastructure.database.models.appointment import Appointment

    query = db.query(Appointment).filter(
        Appointment.clinic_id == clinic_id,
    )

    if period_start:
        query = query.filter(Appointment.scheduled_start >= period_start)
    if period_end:
        query = query.filter(Appointment.scheduled_start <= period_end)

    total = query.count()

    items = (
        query.order_by(Appointment.scheduled_start.desc(), Appointment.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    dto_items: list[AppointmentSummaryDto] = [
        AppointmentSummaryDto(
            id=a.id,
            clinic_id=a.clinic_id,
            pet_name=a.pet.name if a.pet else None,
            owner_name=(
                " ".join(p for p in (a.owner.first_name, a.owner.last_name) if p)
                if a.owner and (a.owner.first_name or a.owner.last_name)
                else None
            ),
            veterinarian_name=(
                a.veterinarian.nombre_completo if a.veterinarian else None
            ),
            appointment_type=a.appointment_type.value,
            status=a.status.value,
            scheduled_start=a.scheduled_start.isoformat(),
            scheduled_end=a.scheduled_end.isoformat(),
        )
        for a in items
    ]

    return PaginatedResponse(
        items=dto_items,  # type: ignore[arg-type]
        total=total,
        page=page,
        size=size,
    )
