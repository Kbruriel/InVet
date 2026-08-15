"""Implementación del repositorio de propietarios."""

from datetime import UTC, datetime, timezone
from typing import Optional, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.owner import Owner, OwnerCreate, OwnerUpdate
from app.domain.repositories.owner_repository import OwnerRepository
from app.infrastructure.database.models.owner import Owner as OwnerModel


class OwnerRepositoryImpl(OwnerRepository):
    """Implementación concreta del repositorio de propietarios."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_domain(self, model: OwnerModel) -> Owner:
        now = datetime.now(timezone.utc)
        created_at = cast(datetime | None, model.created_at) or now
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return Owner(
            id=cast(int, model.id),
            user_id=getattr(model, "user_id", None) or 0,
            nombre=f"{model.first_name} {model.last_name}".strip(),
            email=model.email,
            telefono=model.phone,
            direccion=model.address,
            fecha_creacion=created_at,
        )

    def _from_domain_create(self, data: OwnerCreate) -> OwnerModel:
        now = datetime.now(timezone.utc)
        return OwnerModel(
            first_name=data.nombre.split()[0] if data.nombre else "Unknown",
            last_name=" ".join(data.nombre.split()[1:]) if len(data.nombre.split()) > 1 else "",
            email=data.email,
            phone=data.telefono,
            address=data.direccion,
            clinic_id=0,
            user_id=None,
            created_at=now,
            updated_at=now,
        )

    def _from_domain_update(self, data: OwnerUpdate) -> dict:
        result = {}
        if data.nombre is not None:
            result["first_name"] = data.nombre.split()[0] if data.nombre else "Unknown"
            result["last_name"] = " ".join(data.nombre.split()[1:]) if len(data.nombre.split()) > 1 else ""
        if data.email is not None:
            result["email"] = data.email
        if data.telefono is not None:
            result["phone"] = data.telefono
        if data.direccion is not None:
            result["address"] = data.direccion
        return result

    def create_owner(self, owner: Owner) -> Owner:
        """Crear un nuevo propietario."""
        now = datetime.now(timezone.utc)
        model = OwnerModel(
            first_name=owner.nombre.split()[0] if owner.nombre else "Unknown",
            last_name=" ".join(owner.nombre.split()[1:]) if len(owner.nombre.split()) > 1 else "",
            email=owner.email,
            phone=owner.telefono,
            address=owner.direccion,
            user_id=owner.user_id,
            clinic_id=0,
            created_at=now,
            updated_at=now,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_owner_by_id(self, owner_id: int) -> Optional[Owner]:
        """Obtener un propietario por ID."""
        model = self.db.query(OwnerModel).filter(OwnerModel.id == owner_id).first()
        return self._to_domain(model) if model else None

    def get_owner_by_user_id(self, user_id: int) -> Optional[Owner]:
        """Obtener un propietario vinculado a un usuario."""
        model = (
            self.db.query(OwnerModel)
            .filter(OwnerModel.user_id == user_id)
            .first()
        )
        return self._to_domain(model) if model else None

    def update_owner(self, owner_id: int, data: OwnerUpdate) -> Optional[Owner]:
        """Actualizar campos de un propietario existente."""
        model = (
            self.db.query(OwnerModel)
            .filter(OwnerModel.id == owner_id)
            .first()
        )
        if not model:
            return None

        update_data = self._from_domain_update(data)
        for key, value in update_data.items():
            setattr(model, key, value)
        model.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)
