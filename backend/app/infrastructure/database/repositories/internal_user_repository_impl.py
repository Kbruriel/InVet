"""Implementación del repositorio de usuarios internos para slice 006."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from typing import Any, cast

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.entities.internal_user import InternalUser
from app.domain.repositories.slice006_repositories import InternalUserRepository
from app.infrastructure.database.models.internal_user_model import InternalUser as InternalUserModel


class InternalUserRepositoryImpl(InternalUserRepository):
    """Implementación concreta del repositorio de usuarios internos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_internal_user_by_id(
        self, user_id: int, clinic_id: int
    ) -> InternalUser | None:
        """Obtener un usuario interno por ID y clinic_id con tenant isolation."""
        stmt = (
            select(InternalUserModel)
            .where(InternalUserModel.id == user_id)
            .where(InternalUserModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return self._to_domain(result)

    async def create_internal_user(self, internal_user: InternalUser) -> InternalUser:
        """Crear un nuevo usuario interno."""
        branch_ids_json = json.dumps(internal_user.branch_ids) if internal_user.branch_ids else "[]"
        model = InternalUserModel(
            user_id=internal_user.user_id,
            clinic_id=internal_user.clinic_id,
            nombre=internal_user.nombre,
            rol=internal_user.rol,
            branch_ids=branch_ids_json,
            is_active=internal_user.is_active,
            created_at=internal_user.created_at,
            updated_at=internal_user.updated_at,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    async def update_internal_user(
        self, user_id: int, clinic_id: int, data: dict[str, Any]
    ) -> InternalUser | None:
        """Actualizar campos de un usuario interno existente."""
        stmt = select(InternalUserModel).where(
            InternalUserModel.id == user_id,
            InternalUserModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        for field in ["nombre", "rol", "is_active"]:
            if field in data and data[field] is not None:
                setattr(model, field, data[field])

        if "branch_ids" in data and data["branch_ids"] is not None:
            model.branch_ids = json.dumps(data["branch_ids"])

        model.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    async def deactivate_internal_user(
        self, user_id: int, clinic_id: int
    ) -> InternalUser | None:
        """Inactivar un usuario interno por ID."""
        stmt = select(InternalUserModel).where(
            InternalUserModel.id == user_id,
            InternalUserModel.clinic_id == clinic_id,
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
    ) -> tuple[list[InternalUser], int]:
        """Listar usuarios internos de una clínica con paginación."""
        base_stmt = select(InternalUserModel).where(InternalUserModel.clinic_id == clinic_id)
        if is_active_only:
            base_stmt = base_stmt.where(InternalUserModel.is_active.is_(True))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        query_stmt = base_stmt.offset(offset).limit(size).order_by(InternalUserModel.id)
        results = self.db.execute(query_stmt).scalars().all()
        items = [self._to_domain(r) for r in results]
        return items, total

    async def assign_branch(
        self, user_id: int, clinic_id: int, branch_id: int
    ) -> InternalUser | None:
        """Asignar una sucursal a un usuario interno."""
        stmt = select(InternalUserModel).where(
            InternalUserModel.id == user_id,
            InternalUserModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        current_branches = self._parse_branch_ids(model.branch_ids)
        if branch_id not in current_branches:
            current_branches.append(branch_id)
            model.branch_ids = json.dumps(current_branches)
            model.updated_at = datetime.now(UTC)
            self.db.flush()
            self.db.refresh(model)

        return self._to_domain(model)

    async def unassign_branch(
        self, user_id: int, clinic_id: int, branch_id: int
    ) -> InternalUser | None:
        """Desasignar una sucursal de un usuario interno."""
        stmt = select(InternalUserModel).where(
            InternalUserModel.id == user_id,
            InternalUserModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        current_branches = self._parse_branch_ids(model.branch_ids)
        if branch_id in current_branches:
            current_branches.remove(branch_id)
            model.branch_ids = json.dumps(current_branches)
            model.updated_at = datetime.now(UTC)
            self.db.flush()
            self.db.refresh(model)

        return self._to_domain(model)

    def _to_domain(self, model: InternalUserModel) -> InternalUser:
        """Convertir modelo ORM a entidad de dominio."""
        created_at = cast(datetime | None, model.created_at) or datetime.now(UTC)
        updated_at = cast(datetime | None, model.updated_at) or created_at
        return InternalUser(
            id=cast(int, model.id),
            user_id=cast(int, model.user_id),
            clinic_id=cast(int, model.clinic_id),
            nombre=cast(str, model.nombre),
            rol=cast(str, model.rol),
            branch_ids=self._parse_branch_ids(model.branch_ids),
            is_active=cast(bool, model.is_active),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _parse_branch_ids(self, branch_ids_str: str | None) -> list[int]:
        """Parsear IDs de sucursales desde JSON string."""
        if not branch_ids_str:
            return []
        try:
            result = json.loads(branch_ids_str)
            return [int(bid) for bid in result] if result else []
        except (json.JSONDecodeError, TypeError):
            return []
