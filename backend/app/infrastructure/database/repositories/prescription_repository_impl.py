"""Implementación del repositorio de recetas veterinarias para BE-010."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.prescription import (
    Prescription,
    PrescriptionItem,
    PrescriptionReminder,
    PrescriptionTreatment,
)
from app.domain.repositories.prescription_repository import PrescriptionRepository
from app.infrastructure.database.models.prescription import (
    Prescription as PrescriptionModel,
)
from app.infrastructure.database.models.prescription import (
    PrescriptionItem as PrescriptionItemModel,
)
from app.infrastructure.database.models.prescription import (
    PrescriptionReminder as PrescriptionReminderModel,
)
from app.infrastructure.database.models.prescription import (
    PrescriptionTreatment as PrescriptionTreatmentModel,
)


def _domain_from_model(model: PrescriptionModel) -> Prescription:
    """Convierte un modelo ORM a entidad de dominio (incluye hijos)."""
    return Prescription(
        id=model.id,
        consultation_id=model.consultation_id,
        pet_id=model.pet_id,
        clinic_id=model.clinic_id,
        branch_id=model.branch_id,
        veterinarian_id=model.veterinarian_id,
        diagnosis=model.diagnosis,
        treatment_notes=model.treatment_notes,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
        items=[
            PrescriptionItem(
                id=item.id,
                name=item.name,
                dosage=item.dosage,
                frequency=item.frequency,
                duration=item.duration,
            )
            for item in model.items
        ],
        treatments=[
            PrescriptionTreatment(
                id=treatment.id,
                name=treatment.name,
                instructions=treatment.instructions,
            )
            for treatment in model.treatments
        ],
        reminders=[
            PrescriptionReminder(
                id=reminder.id,
                title=reminder.title,
                due_at=reminder.due_at,
                note=reminder.note,
            )
            for reminder in model.reminders
        ],
    )


class PrescriptionRepositoryImpl(PrescriptionRepository):
    """Implementación concreta del repositorio de recetas veterinarias."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def create_prescription(self, prescription: Prescription) -> Prescription:
        """Crear receta atomica con items, tratamientos y recordatorios."""
        model = PrescriptionModel(
            consultation_id=prescription.consultation_id,
            pet_id=prescription.pet_id,
            clinic_id=prescription.clinic_id,
            branch_id=prescription.branch_id,
            veterinarian_id=prescription.veterinarian_id,
            diagnosis=prescription.diagnosis,
            treatment_notes=prescription.treatment_notes,
            created_by=prescription.created_by,
        )
        model.items = [
            PrescriptionItemModel(
                name=item.name,
                dosage=item.dosage,
                frequency=item.frequency,
                duration=item.duration,
            )
            for item in prescription.items
        ]
        model.treatments = [
            PrescriptionTreatmentModel(
                name=treatment.name, instructions=treatment.instructions
            )
            for treatment in prescription.treatments
        ]
        model.reminders = [
            PrescriptionReminderModel(
                title=reminder.title,
                due_at=reminder.due_at,
                note=reminder.note,
            )
            for reminder in prescription.reminders
        ]
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def get_by_id(
        self, prescription_id: int, clinic_id: int
    ) -> Prescription | None:
        """Obtener receta por ID y clinic_id con tenant isolation."""
        stmt = (
            select(PrescriptionModel)
            .where(PrescriptionModel.id == prescription_id)
            .where(PrescriptionModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return _domain_from_model(result)

    async def exists_by_consultation(
        self, consultation_id: int, clinic_id: int
    ) -> bool:
        """Indica si ya existe receta para esa consulta (tenant isolated)."""
        stmt = (
            select(PrescriptionModel.id)
            .where(PrescriptionModel.consultation_id == consultation_id)
            .where(PrescriptionModel.clinic_id == clinic_id)
        )
        return self.db.execute(stmt).first() is not None

    async def list_by_pet(
        self,
        pet_id: int,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Prescription], int]:
        """Listar recetas de una mascota con paginacion y tenant isolation."""
        base_stmt = (
            select(PrescriptionModel)
            .where(PrescriptionModel.pet_id == pet_id)
            .where(PrescriptionModel.clinic_id == clinic_id)
            .order_by(PrescriptionModel.id.desc())
        )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        paginated_stmt = base_stmt.offset(offset).limit(size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total
