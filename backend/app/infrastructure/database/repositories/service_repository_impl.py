"""Implementación del repositorio de servicios para slice 006."""

from __future__ import annotations

import json
from datetime import datetime, UTC
from typing import Any, cast

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.entities.service import Service
from app.domain.repositories.slice006_repositories import ServiceRepository
from app.infrastructure.database.models.service_model import Service as ServiceModel


class ServiceRepositoryImpl(ServiceRepository):
    """Implementación concreta del repositorio de servicios."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_service_by_id(self, service_id: int, clinic_id: int) -> Service | None:
        """Obtener un servicio por ID y clinic_id con tenant isolation."""
        stmt = (
            select(ServiceModel)
            .where(ServiceModel.id == service_id)
            .where(ServiceModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return self._to_domain(result)

    async def create_service(self, service: Service) -> Service:
        """Crear un nuevo servicio."""
        now = service.created_at
        updated_at = service.updated_at
        model = ServiceModel(
            clinic_id=service.clinic_id,
            name=service.name,
            description=service.description,
            price=int(service.price * 100) if service.price else 0,
            duration_minutes=service.duration_minutes,
            is_active=service.is_active,
            created_at=now,
            updated_at=updated_at,
        )
        # Note: price stored as cents in DB; _to_domain converts back to pesos (divides by 100)
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        domain = self._to_domain(model)
        return domain

    async def update_service(self, service_id: int, clinic_id: int, data: dict[str, Any]) -> Service | None:
        """Actualizar campos de un servicio existente."""
        stmt = select(ServiceModel).where(
            ServiceModel.id == service_id,
            ServiceModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        for field in ["name", "description", "price", "duration_minutes", "is_active"]:
            if field in data and data[field] is not None:
                if field == "price":
                    # Input price is in pesos; store as cents
                    setattr(model, field, int(float(data[field]) * 100))
                else:
                    setattr(model, field, data[field])
        model.updated_at = cast(datetime, model.updated_at) or datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    async def deactivate_service(self, service_id: int, clinic_id: int) -> Service | None:
        """Inactivar un servicio por ID."""
        stmt = select(ServiceModel).where(
            ServiceModel.id == service_id,
            ServiceModel.clinic_id == clinic_id,
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
    ) -> tuple[list[Service], int]:
        """Listar servicios de una clínica con paginación."""
        base_stmt = select(ServiceModel).where(ServiceModel.clinic_id == clinic_id)
        if is_active_only:
            base_stmt = base_stmt.where(ServiceModel.is_active.is_(True))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        query_stmt = base_stmt.offset(offset).limit(size).order_by(ServiceModel.id)
        results = self.db.execute(query_stmt).scalars().all()
        items = [self._to_domain(r) for r in results]
        return items, total

    async def exists_with_name(self, clinic_id: int, name: str) -> bool:
        """Verificar si ya existe un servicio con el mismo nombre en la clínica."""
        stmt = (
            select(func.count())
            .select_from(ServiceModel)
            .where(
                ServiceModel.clinic_id == clinic_id,
                ServiceModel.name.ilike(name),
                ServiceModel.is_active.is_(True),
            )
        )
        return bool(self.db.execute(stmt).scalar() > 0)

    def _to_domain(self, model: ServiceModel) -> Service:
        """Convertir modelo ORM a entidad de dominio.

        Precio: DB almacena en centavos (Integer), el dominio usa pesos (float).
        La conversión inversa divide por 100 para mostrar el precio correcto al frontend.
        """
        created_at = cast(datetime | None, model.created_at) or datetime.now(UTC)
        updated_at = cast(datetime | None, model.updated_at) or created_at
        price = (model.price / 100.0) if model.price else 0.0
        return Service(
            id=cast(int, model.id),
            clinic_id=cast(int, model.clinic_id),
            name=cast(str, model.name),
            description=cast(str | None, model.description),
            price=price,
            duration_minutes=cast(int, model.duration_minutes),
            is_active=cast(bool, model.is_active),
            created_at=created_at,
            updated_at=updated_at,
        )
