"""Caso de uso: conteo de mascotas activas (BE-015-T04).

Depende de: BE-015-T01 (schemas Pydantic) y modelos Pet/Owner.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.api.v1.schemas.report_schemas import PetCountDto


def report_pets_count(
    db: Session,
    clinic_id: int,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> PetCountDto:
    """Devuelve el conteo de mascotas activas por cl\u00ednica.\n\n
    Args:\n        db: DB session (inyectada).\n        clinic_id: ID de la cl\u00ednica (tenant isolation).\n        period_start: Filtro por fecha inicio (opcional).\n        period_end: Filtro por fecha fin (opcional).\n\n    Returns:\n        PetCountDto plano con {clinic_id, active_count}.
    """
    from app.infrastructure.database.models.owner import Owner
    from app.infrastructure.database.models.pet import Pet

    query = (
        db.query(Pet)
        .join(Owner, Pet.owner_id == Owner.id)
        .filter(
            Owner.clinic_id == clinic_id,
            Pet.is_active == True,  # noqa: E712
        )
    )

    if period_start:
        query = query.filter(Pet.created_at >= period_start)
    if period_end:
        query = query.filter(Pet.updated_at <= period_end)

    count = query.count()

    return PetCountDto(clinic_id=clinic_id, active_count=count)
