"""Implementación del repositorio de clínicas."""

from datetime import datetime
from typing import cast

from sqlalchemy.orm import Session

from app.domain.entities.clinic import Clinic
from app.domain.repositories.clinic_repository import ClinicRepository
from app.infrastructure.database.models.clinic import Clinic as ClinicModel


class ClinicRepositoryImpl(ClinicRepository):
    """Implementación concreta del repositorio de clínicas."""

    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, clinic: ClinicModel) -> Clinic:
        timestamp = datetime.utcnow()
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

    async def search_clinics(
        self,
        location: str | None = None,
        service_type: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Clinic]:
        """Buscar clínicas según criterios especificados."""
        # Calcular offset
        offset = (page - 1) * size

        # Construir consulta
        query = self.db.query(ClinicModel)

        # Solo mostrar clínicas activas
        query = query.filter(ClinicModel.is_active.is_(True))

        # Filtrar por ubicación si se proporciona
        if location:
            location_lower = location.lower()
            query = query.filter(
                (ClinicModel.city.ilike(f"%{location_lower}%"))
                | (ClinicModel.address.ilike(f"%{location_lower}%"))
            )

        # Ejecutar consulta con paginación
        clinics = query.offset(offset).limit(size).all()

        # Convertir resultados a entidades Pydantic
        return [self._to_domain(clinic) for clinic in clinics]

    async def get_clinic_count(
        self, location: str | None = None, service_type: str | None = None
    ) -> int:
        """Obtener el número total de clínicas que coinciden con los criterios."""
        # Construir consulta
        query = self.db.query(ClinicModel)

        # Solo mostrar clínicas activas
        query = query.filter(ClinicModel.is_active.is_(True))

        # Filtrar por ubicación si se proporciona
        if location:
            location_lower = location.lower()
            query = query.filter(
                (ClinicModel.city.ilike(f"%{location_lower}%"))
                | (ClinicModel.address.ilike(f"%{location_lower}%"))
            )

        # Devolver el conteo
        return query.count()
