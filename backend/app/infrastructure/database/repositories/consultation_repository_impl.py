"""Implementación del repositorio de consultas médicas para BE-009."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.consultation import Consultation
from app.domain.repositories.consultation_repository import ConsultationRepository
from app.infrastructure.database.models.consultation import (
    Consultation as ConsultationModel,
)


def _domain_from_model(model: ConsultationModel) -> Consultation:
    """Convierte un modelo ORM a entidad de dominio."""
    return Consultation(
        id=model.id,
        appointment_id=model.appointment_id,
        pet_id=model.pet_id,
        clinic_id=model.clinic_id,
        branch_id=model.branch_id,
        veterinarian_id=model.veterinarian_id,
        history=model.history,
        diagnosis=model.diagnosis,
        recommendations=model.recommendations,
        created_by=model.created_by,
        updated_at=model.updated_at,
    )


class ConsultationRepositoryImpl(ConsultationRepository):
    """Implementación concreta del repositorio de consultas médicas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def create_consultation(self, consultation: Consultation) -> Consultation:
        """Crear una nueva consulta."""
        model = ConsultationModel(
            appointment_id=consultation.appointment_id,
            pet_id=consultation.pet_id,
            clinic_id=consultation.clinic_id,
            branch_id=consultation.branch_id,
            veterinarian_id=consultation.veterinarian_id,
            history=consultation.history,
            diagnosis=consultation.diagnosis,
            recommendations=consultation.recommendations,
            created_by=consultation.created_by,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def get_by_id(
        self, consultation_id: int, clinic_id: int
    ) -> Consultation | None:
        """Obtener una consulta por ID y clinic_id con tenant isolation."""
        stmt = (
            select(ConsultationModel)
            .where(ConsultationModel.id == consultation_id)
            .where(ConsultationModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return _domain_from_model(result)

    async def get_by_appointment_id(
        self, appointment_id: int, clinic_id: int
    ) -> Consultation | None:
        """Obtener la consulta asociada a una cita."""
        stmt = (
            select(ConsultationModel)
            .where(ConsultationModel.appointment_id == appointment_id)
            .where(ConsultationModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return _domain_from_model(result)

    async def list_by_pet(
        self,
        pet_id: int,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Consultation], int]:
        """Listar consultas de una mascota con paginación."""
        base_stmt = (
            select(ConsultationModel)
            .where(ConsultationModel.pet_id == pet_id)
            .where(ConsultationModel.clinic_id == clinic_id)
            .order_by(ConsultationModel.id.desc())
        )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        paginated_stmt = base_stmt.offset(offset).limit(size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total

    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        pet_id: int | None = None,
    ) -> tuple[list[Consultation], int]:
        """Listar consultas de una clínica con filtros y paginación."""
        conditions = [ConsultationModel.clinic_id == clinic_id]
        if pet_id is not None:
            conditions.append(ConsultationModel.pet_id == pet_id)

        base_stmt = (
            select(ConsultationModel)
            .where(*conditions)
            .order_by(ConsultationModel.id.desc())
        )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        paginated_stmt = base_stmt.offset(offset).limit(size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total
