"""Implementación del repositorio de veterinarios para slice 006."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, cast

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.entities.veterinarian import (
    Veterinarian,
    VeterinarianServiceAssignment,
)
from app.domain.repositories.slice006_repositories import VeterinarianRepository
from app.infrastructure.database.models.veterinarian_model import Veterinarian as VeterinarianModel


class VeterinarianRepositoryImpl(VeterinarianRepository):
    """Implementación concreta del repositorio de veterinarios."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_veterinarian_by_id(self, vet_id: int, clinic_id: int) -> Veterinarian | None:
        """Obtener un veterinario por ID y clinic_id con tenant isolation."""
        stmt = (
            select(VeterinarianModel)
            .where(VeterinarianModel.id == vet_id)
            .where(VeterinarianModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return self._to_domain(result)

    async def create_veterinarian(self, veterinarian: Veterinarian) -> Veterinarian:
        """Crear un nuevo veterinario."""
        model = VeterinarianModel(
            clinic_id=veterinarian.clinic_id,
            nombre_completo=veterinarian.nombre_completo,
            licencia_profesional=veterinarian.licencia_profesional,
            especialidad=veterinarian.especialidad,
            telefono=veterinarian.telefono,
            email=veterinarian.email,
            is_active=veterinarian.is_active,
            created_at=veterinarian.created_at,
            updated_at=veterinarian.updated_at,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    async def update_veterinarian(
        self, vet_id: int, clinic_id: int, data: dict[str, Any]
    ) -> Veterinarian | None:
        """Actualizar campos de un veterinario existente."""
        stmt = select(VeterinarianModel).where(
            VeterinarianModel.id == vet_id,
            VeterinarianModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        for field in ["nombre_completo", "licencia_profesional", "especialidad", "telefono", "email", "is_active"]:
            if field in data and data[field] is not None:
                setattr(model, field, data[field])
        model.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    async def deactivate_veterinarian(self, vet_id: int, clinic_id: int) -> Veterinarian | None:
        """Inactivar un veterinario por ID."""
        stmt = select(VeterinarianModel).where(
            VeterinarianModel.id == vet_id,
            VeterinarianModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        model.is_active = False
        model.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[Veterinarian], int]:
        """Listar veterinarios de una clínica con paginación."""
        base_stmt = select(VeterinarianModel).where(VeterinarianModel.clinic_id == clinic_id)
        if is_active_only:
            base_stmt = base_stmt.where(VeterinarianModel.is_active.is_(True))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        query_stmt = base_stmt.offset(offset).limit(size).order_by(VeterinarianModel.id)
        results = self.db.execute(query_stmt).scalars().all()
        items = [self._to_domain(r) for r in results]
        return items, total

    async def exists_with_license(
        self, clinic_id: int, license_number: str
    ) -> bool:
        """Verificar si ya existe un veterinario con la misma licencia en la clínica."""
        stmt = (
            select(func.count())
            .select_from(VeterinarianModel)
            .where(
                VeterinarianModel.clinic_id == clinic_id,
                VeterinarianModel.licencia_profesional.ilike(license_number),
                VeterinarianModel.is_active.is_(True),
            )
        )
        return bool(self.db.execute(stmt).scalar() > 0)

    async def get_assigned_services(
        self, vet_id: int, clinic_id: int
    ) -> list[VeterinarianServiceAssignment]:
        """Obtener servicios asignados a un veterinario."""
        from app.infrastructure.database.models.assignment_model import VeterinarianServiceAssignment as AssignmentModel

        stmt = (
            select(AssignmentModel)
            .where(AssignmentModel.veterinarian_id == vet_id)
            .where(AssignmentModel.clinic_id == clinic_id)
            .order_by(AssignmentModel.id)
        )
        results = self.db.execute(stmt).scalars().all()
        return [self._to_assignment(r) for r in results]

    def _to_domain(self, model: VeterinarianModel) -> Veterinarian:
        """Convertir modelo ORM a entidad de dominio."""
        created_at = cast(datetime | None, model.created_at) or datetime.now(UTC)
        updated_at = cast(datetime | None, model.updated_at) or created_at
        return Veterinarian(
            id=cast(int, model.id),
            clinic_id=cast(int, model.clinic_id),
            nombre_completo=cast(str, model.nombre_completo),
            licencia_profesional=cast(str, model.licencia_profesional),
            especialidad=cast(str, model.especialidad),
            telefono=cast(str | None, model.telefono),
            email=cast(str | None, model.email),
            is_active=cast(bool, model.is_active),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _to_assignment(self, model) -> VeterinarianServiceAssignment:
        """Convertir modelo de asignación a entidad de dominio."""
        assigned_at = cast(datetime | None, model.assigned_at) or datetime.now(UTC)
        return VeterinarianServiceAssignment(
            id=cast(int, model.id),
            veterinarian_id=cast(int, model.veterinarian_id),
            service_id=cast(int, model.service_id),
            clinic_id=cast(int, model.clinic_id),
            assigned_at=assigned_at,
        )
