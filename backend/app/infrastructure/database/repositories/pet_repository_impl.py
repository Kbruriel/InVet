"""Implementación del repositorio para mascotas."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.repositories.pet_repository import PetRepository
from app.infrastructure.database.models.pet import Pet


class PetRepositoryImpl(PetRepository):
    """Implementación concreta del repositorio para mascotas."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_pet(self, pet_id: int) -> Optional[Pet]:
        """Obtiene una mascota por ID."""
        return self.db.query(Pet).filter(Pet.id == pet_id).first()

    def get_pets(self, skip: int = 0, limit: int = 100) -> List[Pet]:
        """Obtiene múltiples mascotas con paginación."""
        return self.db.query(Pet).offset(skip).limit(limit).all()

    def create_pet(self, pet_data: dict) -> Pet:
        """Crea una nueva mascota."""
        db_pet = Pet(**pet_data)
        self.db.add(db_pet)
        self.db.commit()
        self.db.refresh(db_pet)
        return db_pet

    def update_pet(self, pet_id: int, pet_data: dict) -> Optional[Pet]:
        """Actualiza una mascota existente."""
        db_pet = self.get_pet(pet_id)
        if db_pet:
            for key, value in pet_data.items():
                setattr(db_pet, key, value)
            self.db.commit()
            self.db.refresh(db_pet)
        return db_pet

    def delete_pet(self, pet_id: int) -> bool:
        """Elimina una mascota."""
        db_pet = self.get_pet(pet_id)
        if db_pet:
            self.db.delete(db_pet)
            self.db.commit()
            return True
        return False

    def get_pets_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Pet]:
        """Obtiene mascotas por propietario."""
        return self.db.query(Pet).filter(Pet.owner_id == owner_id).offset(skip).limit(limit).all()