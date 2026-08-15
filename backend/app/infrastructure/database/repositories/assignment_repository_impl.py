"""Implementación del repositorio de asignaciones para slice 006."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.veterinarian import VeterinarianServiceAssignment
from app.domain.repositories.slice006_repositories import AssignmentRepository
from app.infrastructure.database.models.assignment_model import (
    VeterinarianServiceAssignment as AssignmentModel,
)
from app.infrastructure.database.models.service_model import Service as ServiceModel
from app.infrastructure.database.models.veterinarian_model import (
    Veterinarian as VeterinarianModel,
)


class AssignmentRepositoryImpl(AssignmentRepository):
    """Implementación concreta del repositorio de asignaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def assign_service(
        self, vet_id: int, service_id: int, clinic_id: int
    ) -> VeterinarianServiceAssignment | None:
        """Asignar un servicio a un veterinario."""
        # Validar que el veterinario existe y pertenece a la misma clínica
        vet_stmt = select(VeterinarianModel.id).where(
            VeterinarianModel.id == vet_id,
            VeterinarianModel.clinic_id == clinic_id,
        )
        vet_exists = bool(self.db.execute(vet_stmt).scalar())
        if not vet_exists:
            return None

        # Validar que el servicio existe y pertenece a la misma clínica
        svc_stmt = select(ServiceModel.id).where(
            ServiceModel.id == service_id,
            ServiceModel.clinic_id == clinic_id,
        )
        svc_exists = bool(self.db.execute(svc_stmt).scalar())
        if not svc_exists:
            return None

        # Verificar que no existe ya la asignación
        existing_stmt = select(AssignmentModel).where(
            AssignmentModel.veterinarian_id == vet_id,
            AssignmentModel.service_id == service_id,
            AssignmentModel.clinic_id == clinic_id,
        )
        existing = self.db.execute(existing_stmt).scalar_one_or_none()
        if existing is not None:
            return None

        assignment = AssignmentModel(
            veterinarian_id=vet_id,
            service_id=service_id,
            clinic_id=clinic_id,
            assigned_at=datetime.now(UTC),
        )
        self.db.add(assignment)
        self.db.flush()
        self.db.refresh(assignment)
        return self._to_domain(assignment)

    async def unassign_service(
        self, vet_id: int, service_id: int, clinic_id: int
    ) -> bool:
        """Desasignar un servicio de un veterinario."""
        stmt = select(AssignmentModel).where(
            AssignmentModel.veterinarian_id == vet_id,
            AssignmentModel.service_id == service_id,
            AssignmentModel.clinic_id == clinic_id,
        )
        assignment = self.db.execute(stmt).scalar_one_or_none()
        if assignment is None:
            return False
        self.db.delete(assignment)
        self.db.flush()
        return True

    async def get_assignments_by_veterinarian(
        self, vet_id: int, clinic_id: int
    ) -> list[VeterinarianServiceAssignment]:
        """Obtener todas las asignaciones de un veterinario."""
        stmt = (
            select(AssignmentModel)
            .where(AssignmentModel.veterinarian_id == vet_id)
            .where(AssignmentModel.clinic_id == clinic_id)
            .order_by(AssignmentModel.id)
        )
        results = self.db.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in results]

    def _to_domain(self, model: AssignmentModel) -> VeterinarianServiceAssignment:
        """Convertir modelo ORM a entidad de dominio."""
        assigned_at = cast(datetime | None, model.assigned_at) or datetime.now(UTC)
        return VeterinarianServiceAssignment(
            id=cast(int, model.id),
            veterinarian_id=cast(int, model.veterinarian_id),
            service_id=cast(int, model.service_id),
            clinic_id=cast(int, model.clinic_id),
            assigned_at=assigned_at,
        )
