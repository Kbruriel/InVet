"""Implementación del repositorio para propietarios."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.repositories.owner_repository import OwnerRepository
from app.infrastructure.database.models.owner import Owner


class OwnerRepositoryImpl(OwnerRepository):
    """Implementación concreta del repositorio para propietarios."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_owner(self, owner_id: int) -> Optional[Owner]:
        """Obtiene un propietario por ID."""
        return self.db.query(Owner).filter(Owner.id == owner_id).first()

    def get_owners(self, skip: int = 0, limit: int = 100) -> List[Owner]:
        """Obtiene múltiples propietarios con paginación."""
        return self.db.query(Owner).offset(skip).limit(limit).all()

    def create_owner(self, owner_data: dict) -> Owner:
        """Crea un nuevo propietario."""
        db_owner = Owner(**owner_data)
        self.db.add(db_owner)
        self.db.commit()
        self.db.refresh(db_owner)
        return db_owner

    def update_owner(self, owner_id: int, owner_data: dict) -> Optional[Owner]:
        """Actualiza un propietario existente."""
        db_owner = self.get_owner(owner_id)
        if db_owner:
            for key, value in owner_data.items():
                setattr(db_owner, key, value)
            self.db.commit()
            self.db.refresh(db_owner)
        return db_owner

    def delete_owner(self, owner_id: int) -> bool:
        """Elimina un propietario."""
        db_owner = self.get_owner(owner_id)
        if db_owner:
            self.db.delete(db_owner)
            self.db.commit()
            return True
        return False

    def get_owners_by_clinic(
        self, clinic_id: int, skip: int = 0, limit: Optional[int] = 100
    ) -> List[Owner]:
        """Obtiene propietarios por clínica."""
        query = self.db.query(Owner).filter(Owner.clinic_id == clinic_id)
        if skip:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()
