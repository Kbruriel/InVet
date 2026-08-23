"""Schemas Pydantic para recetas veterinarias (BE-010)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.prescription import (
    PrescriptionCreate as PrescriptionCreateDomain,
)
from app.domain.entities.prescription import (
    PrescriptionItem,
    PrescriptionReminder,
    PrescriptionTreatment,
)
from app.domain.entities.prescription import (
    PrescriptionItemInput as PrescriptionItemInputDomain,
)
from app.domain.entities.prescription import (
    PrescriptionReminderInput as PrescriptionReminderInputDomain,
)
from app.domain.entities.prescription import (
    PrescriptionTreatmentInput as PrescriptionTreatmentInputDomain,
)


class PrescriptionItemCreate(BaseModel):
    """Medicamento a incluir en la receta."""

    name: str = Field(..., min_length=1, max_length=200)
    dosage: str | None = Field(None, max_length=200)
    frequency: str | None = Field(None, max_length=200)
    duration: str | None = Field(None, max_length=200)


class PrescriptionTreatmentCreate(BaseModel):
    """Tratamiento a incluir en la receta."""

    name: str = Field(..., min_length=1, max_length=300)
    instructions: str = Field(default="", max_length=2000)


class PrescriptionReminderCreate(BaseModel):
    """Recordatorio a incluir en la receta."""

    title: str = Field(..., min_length=1, max_length=300)
    due_at: datetime | None = None
    note: str | None = Field(None, max_length=1000)


class PrescriptionCreate(BaseModel):
    """Schema para crear una receta desde el frontend.

    Reglas:
    - ``consultation_id`` debe referir a una consulta cuya cita esté ``completed``.
    - ``pet_id`` debe coincidir con la mascota de la consulta.
    - ``clinic_id`` es opcional; el backend lo resuelve del usuario autenticado.
    """

    consultation_id: int = Field(..., gt=0, description="ID de la consulta completada")
    pet_id: int = Field(..., gt=0, description="ID de la mascota")
    clinic_id: int | None = Field(
        None, gt=0, description="ID de la clínica (opcional; se resuelve del usuario)"
    )
    veterinarian_id: int | None = Field(
        None, ge=1, description="ID del veterinario que prescribió (opcional)"
    )
    diagnosis: str = Field(..., min_length=1, max_length=2000)
    treatment_notes: str | None = Field(
        None, max_length=3000, description="Notas de tratamiento opcionales"
    )
    items: list[PrescriptionItemCreate] = Field(default_factory=list, max_length=50)
    treatments: list[PrescriptionTreatmentCreate] = Field(
        default_factory=list, max_length=50
    )
    reminders: list[PrescriptionReminderCreate] = Field(
        default_factory=list, max_length=50
    )


class PrescriptionRead(BaseModel):
    """Schema de respuesta para una receta veterinaria."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    consultation_id: int
    pet_id: int
    clinic_id: int
    branch_id: int | None = None
    veterinarian_id: int | None = None
    diagnosis: str
    treatment_notes: str
    created_by: int | None = None
    items: list[PrescriptionItem] = []
    treatments: list[PrescriptionTreatment] = []
    reminders: list[PrescriptionReminder] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PrescriptionPage(BaseModel):
    """Respuesta paginada de recetas veterinarias."""

    items: list[PrescriptionRead]
    meta: dict


def to_domain_create(
    payload: PrescriptionCreate,
    clinic_id: int,
    created_by: int | None,
) -> PrescriptionCreateDomain:
    """Convierte el payload API al DTO de dominio del caso de uso."""
    return PrescriptionCreateDomain(
        consultation_id=payload.consultation_id,
        pet_id=payload.pet_id,
        clinic_id=clinic_id,
        veterinarian_id=payload.veterinarian_id,
        diagnosis=payload.diagnosis,
        treatment_notes=payload.treatment_notes or "",
        items=[PrescriptionItemInputDomain(**i.model_dump()) for i in payload.items],
        treatments=[
            PrescriptionTreatmentInputDomain(**t.model_dump())
            for t in payload.treatments
        ],
        reminders=[
            PrescriptionReminderInputDomain(**r.model_dump()) for r in payload.reminders
        ],
        created_by=created_by,
    )
