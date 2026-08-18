"""Implementación del repositorio de clínicas con soporte CRUD administrativo."""

import unicodedata
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.entities.clinic import Clinic
from app.domain.repositories.clinic_repository import ClinicRepository
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.service_model import Service as ServiceModel


class ClinicRepositoryImpl(ClinicRepository):
    """Implementación concreta del repositorio de clínicas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_domain(self, clinic: ClinicModel) -> Clinic:
        timestamp = datetime.now(UTC)
        created_at = cast(datetime | None, clinic.created_at) or timestamp
        updated_at = cast(datetime | None, clinic.updated_at) or created_at

        return Clinic(
            id=cast(int, clinic.id),
            name=cast(str, clinic.name),
            description=cast(str | None, clinic.description),
            address=cast(str, clinic.address),
            city=cast(str, clinic.city),
            state=cast(str, clinic.state),
            country=cast(str, clinic.country),
            postal_code=cast(str, clinic.postal_code),
            phone=cast(str | None, clinic.phone),
            email=cast(str | None, clinic.email),
            is_active=cast(bool, clinic.is_active),
            created_at=created_at,
            updated_at=updated_at,
        )

    def _from_domain(self, clinic: Clinic) -> ClinicModel:
        now = datetime.now(UTC)
        return ClinicModel(
            id=getattr(clinic, "id", 0),
            name=clinic.name,
            description=clinic.description,
            address=clinic.address,
            city=clinic.city,
            state=clinic.state,
            country=clinic.country,
            postal_code=clinic.postal_code,
            phone=clinic.phone,
            email=clinic.email,
            is_active=clinic.is_active,
            created_at=getattr(clinic, "created_at", now) or now,
            updated_at=getattr(clinic, "updated_at", now) or now,
        )

    @staticmethod
    def _normalize_text(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        return normalized.encode("ascii", "ignore").decode("ascii").lower().strip()

    @staticmethod
    def _normalized_sql_text(column):
        normalized = func.lower(column)
        for source, target in (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ü", "u"),
            ("ñ", "n"),
        ):
            normalized = func.replace(normalized, source, target)
        return normalized

    # --- Métodos públicos (BE-004) ---

    async def search_clinics(
        self,
        location: str | None = None,
        service_type: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Clinic]:
        """Buscar clínicas según criterios especificados."""
        offset = (page - 1) * size

        query = select(ClinicModel).filter(ClinicModel.is_active.is_(True))

        if location:
            location_lower = location.lower()
            query = query.where(
                (ClinicModel.city.ilike(f"%{location_lower}%"))
                | (ClinicModel.address.ilike(f"%{location_lower}%"))
            )

        if service_type:
            service_type_normalized = self._normalize_text(service_type)
            service_name = self._normalized_sql_text(ServiceModel.name)
            service_description = self._normalized_sql_text(ServiceModel.description)
            query = query.where(
                select(1)
                .select_from(ServiceModel)
                .where(
                    ServiceModel.clinic_id == ClinicModel.id,
                    ServiceModel.is_active.is_(True),
                    or_(
                        service_name.like(f"%{service_type_normalized}%"),
                        service_description.like(f"%{service_type_normalized}%"),
                    ),
                )
                .exists()
            )

        query = query.order_by(ClinicModel.id).offset(offset).limit(size)
        result = self.db.execute(query)
        clinics = result.scalars().all()

        return [self._to_domain(clinic) for clinic in clinics]

    async def get_clinic_count(
        self, location: str | None = None, service_type: str | None = None
    ) -> int:
        """Obtener el número total de clínicas que coinciden con los criterios."""
        query = select(ClinicModel).filter(ClinicModel.is_active.is_(True))

        if location:
            location_lower = location.lower()
            query = query.where(
                (ClinicModel.city.ilike(f"%{location_lower}%"))
                | (ClinicModel.address.ilike(f"%{location_lower}%"))
            )

        if service_type:
            service_type_normalized = self._normalize_text(service_type)
            service_name = self._normalized_sql_text(ServiceModel.name)
            service_description = self._normalized_sql_text(ServiceModel.description)
            query = query.where(
                select(1)
                .select_from(ServiceModel)
                .where(
                    ServiceModel.clinic_id == ClinicModel.id,
                    ServiceModel.is_active.is_(True),
                    or_(
                        service_name.like(f"%{service_type_normalized}%"),
                        service_description.like(f"%{service_type_normalized}%"),
                    ),
                )
                .exists()
            )

        result = self.db.execute(query)
        return len(result.scalars().all())

    async def get_clinic_by_id(self, clinic_id: int) -> Clinic | None:
        """Obtener una clínica por ID o None si no existe."""
        clinic_model = (
            self.db.query(ClinicModel).filter(ClinicModel.id == clinic_id).first()
        )
        if clinic_model is None:
            return None
        return self._to_domain(clinic_model)

    # --- CRUD administrativo (BE-005) ---

    async def create_clinic(self, clinic: Clinic) -> Clinic:
        """Crear una nueva clínica. Retorna la entidad con ID asignado."""
        now = datetime.utcnow()
        model = ClinicModel(
            name=clinic.name,
            description=clinic.description,
            address=clinic.address,
            city=clinic.city,
            state=clinic.state,
            country=clinic.country,
            postal_code=clinic.postal_code,
            phone=clinic.phone,
            email=clinic.email,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)

        clinic.id = model.id
        return clinic

    async def update_clinic(
        self, clinic_id: int, data: dict[str, Any]
    ) -> Clinic | None:
        """Actualizar campos de una clínica existente."""
        clinic_model = (
            self.db.query(ClinicModel).filter(ClinicModel.id == clinic_id).first()
        )
        if clinic_model is None:
            return None

        for key, value in data.items():
            if hasattr(clinic_model, key) and value is not None:
                setattr(clinic_model, key, value)

        clinic_model.updated_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(clinic_model)

        return self._to_domain(clinic_model)

    async def deactivate_clinic(self, clinic_id: int) -> Clinic | None:
        """Inactivar una clínica por ID."""
        clinic_model = (
            self.db.query(ClinicModel).filter(ClinicModel.id == clinic_id).first()
        )
        if clinic_model is None:
            return None

        clinic_model.is_active = False
        clinic_model.updated_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(clinic_model)

        return self._to_domain(clinic_model)

    async def activate_clinic(self, clinic_id: int) -> Clinic | None:
        """Reactivar una clínica inactiva por ID."""
        clinic_model = (
            self.db.query(ClinicModel).filter(ClinicModel.id == clinic_id).first()
        )
        if clinic_model is None:
            return None

        clinic_model.is_active = True
        clinic_model.updated_at = datetime.utcnow()
        self.db.flush()
        self.db.refresh(clinic_model)

        return self._to_domain(clinic_model)

    async def list_clinics_by_tenant(
        self,
        tenant_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Clinic], int]:
        """Listar clínicas de un tenant con paginación."""
        offset = (page - 1) * size

        # Contar total
        count_query = select(ClinicModel).filter(
            ClinicModel.id.in_(
                self.db.query(ClinicModel.id)
                .filter(
                    getattr(ClinicModel, "tenant_id", None) == tenant_id
                    if hasattr(ClinicModel, "tenant_id")
                    else True
                )
                .subquery()
            )
        )
        total_result = self.db.execute(count_query)
        total = len(total_result.scalars().all())

        # Obtener página
        query = (
            select(ClinicModel)
            .filter(
                getattr(ClinicModel, "tenant_id", None) == tenant_id
                if hasattr(ClinicModel, "tenant_id")
                else ClinicModel.is_active.is_(True)
            )
            .offset(offset)
            .limit(size)
        )

        result = self.db.execute(query)
        clinics = result.scalars().all()

        return ([self._to_domain(c) for c in clinics], total)
