"""Implementación del repositorio de veterinarios."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.veterinarian import (
    Veterinarian,
    VeterinarianCreate,
    VeterinarianUpdate,
)
from app.domain.repositories.veterinarian_repo import VeterinarianRepository
from app.infrastructure.database.models.veterinarian import (
    Veterinarian as VeterinarianDB,
)


class VeterinarianRepositoryImpl(VeterinarianRepository):
    """Implementación del repositorio de veterinarios."""

    def __init__(self, db: Session):
        self.db = db

    def create_veterinarian(
        self, veterinarian_data: VeterinarianCreate
    ) -> Veterinarian:
        """Crea un nuevo veterinario."""
        db_veterinarian = VeterinarianDB(
            branch_id=veterinarian_data.branch_id,
            first_name=veterinarian_data.name,
            last_name=veterinarian_data.last_name,
            specialty=veterinarian_data.specialty,
            email=veterinarian_data.email,
            phone=veterinarian_data.phone,
            license_number=veterinarian_data.license_number,
            is_active=veterinarian_data.is_active,
        )
        self.db.add(db_veterinarian)
        self.db.commit()
        self.db.refresh(db_veterinarian)
        return self._db_to_domain(db_veterinarian)

    def get_veterinarian(self, veterinarian_id: int) -> Optional[Veterinarian]:
        """Obtiene un veterinario por ID."""
        db_veterinarian = (
            self.db.query(VeterinarianDB)
            .filter(VeterinarianDB.id == veterinarian_id)
            .first()
        )
        return self._db_to_domain(db_veterinarian) if db_veterinarian else None

    def get_veterinarians(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Veterinarian]:
        """Obtiene una lista de veterinarios para una sucursal."""
        db_veterinarians = (
            self.db.query(VeterinarianDB)
            .filter(VeterinarianDB.branch_id == branch_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [
            self._db_to_domain(db_veterinarian) for db_veterinarian in db_veterinarians
        ]

    def update_veterinarian(
        self, veterinarian_id: int, veterinarian_data: VeterinarianUpdate
    ) -> Optional[Veterinarian]:
        """Actualiza un veterinario existente."""
        db_veterinarian = (
            self.db.query(VeterinarianDB)
            .filter(VeterinarianDB.id == veterinarian_id)
            .first()
        )
        if not db_veterinarian:
            return None

        updates = veterinarian_data.model_dump(exclude_unset=True)
        if "name" in updates:
            updates["first_name"] = updates.pop("name")

        for key, value in updates.items():
            setattr(db_veterinarian, key, value)

        self.db.commit()
        self.db.refresh(db_veterinarian)
        return self._db_to_domain(db_veterinarian)

    def delete_veterinarian(self, veterinarian_id: int) -> bool:
        """Elimina un veterinario."""
        db_veterinarian = (
            self.db.query(VeterinarianDB)
            .filter(VeterinarianDB.id == veterinarian_id)
            .first()
        )
        if not db_veterinarian:
            return False

        self.db.delete(db_veterinarian)
        self.db.commit()
        return True

    def _db_to_domain(self, db_veterinarian: VeterinarianDB) -> Veterinarian:
        """Convierte un modelo de base de datos a entidad de dominio."""
        return Veterinarian(
            id=db_veterinarian.id,
            branch_id=db_veterinarian.branch_id,
            name=db_veterinarian.first_name,
            last_name=db_veterinarian.last_name,
            specialty=db_veterinarian.specialty,
            email=db_veterinarian.email,
            phone=db_veterinarian.phone,
            license_number=db_veterinarian.license_number,
            is_active=db_veterinarian.is_active,
            created_at=db_veterinarian.created_at,
            updated_at=db_veterinarian.updated_at,
        )
