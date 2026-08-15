"""Implementación del repositorio de mascotas."""

from datetime import UTC, datetime
from typing import cast

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.owner import Pet, PetHistoryEntry, PetUpdate
from app.domain.repositories.owner_repository import PetRepository
from app.infrastructure.database.models.pet import Pet as PetModel


class PetRepositoryImpl(PetRepository):
    """Implementación concreta del repositorio de mascotas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_domain(self, model: PetModel) -> Pet:
        now = datetime.now(UTC)
        dob = cast(datetime | None, model.date_of_birth)
        if dob and dob.tzinfo is None:
            dob = dob.replace(tzinfo=UTC)

        edad = 0
        if dob:
            today = datetime.now(UTC).date()
            edad = (today.year - dob.year) - (
                (today.month, today.day) < (dob.month, dob.day)
            )

        peso_val = float(model.weight) if model.weight else None

        return Pet(
            id=cast(int, model.id),
            owner_id=cast(int, model.owner_id),
            nombre=model.name,
            especie=model.species,
            raza=model.breed or "",
            edad=edad,
            peso=peso_val,
            fecha_nacimiento=dob,
        )

    def create_pet(self, pet: Pet) -> Pet:
        """Crear una nueva mascota."""
        dob = pet.fecha_nacimiento
        if dob and dob.tzinfo is None:
            dob = dob.replace(tzinfo=UTC)

        model = PetModel(
            owner_id=pet.owner_id,
            name=pet.nombre,
            species=pet.especie,
            breed=pet.raza,
            weight=str(pet.peso) if pet.peso is not None else None,
            date_of_birth=dob,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_pet_by_id(self, pet_id: int) -> Pet | None:
        """Obtener una mascota por ID (solo activas)."""
        model = (
            self.db.query(PetModel)
            .filter(PetModel.id == pet_id, PetModel.is_active.is_(True))
            .first()
        )
        return self._to_domain(model) if model else None

    def get_pets_by_owner(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Pet], int]:
        """Obtener mascotas paginadas de un propietario."""
        offset = (page - 1) * size

        total_query = self.db.query(func.count(PetModel.id)).filter(
            PetModel.owner_id == owner_id, PetModel.is_active.is_(True)
        )
        total = total_query.scalar() or 0

        query = (
            self.db.query(PetModel)
            .filter(PetModel.owner_id == owner_id, PetModel.is_active.is_(True))
            .offset(offset)
            .limit(size)
            .all()
        )
        return [self._to_domain(m) for m in query], total

    def update_pet(self, pet_id: int, data: PetUpdate) -> Pet | None:
        """Actualizar campos de una mascota existente."""
        model = self.db.query(PetModel).filter(PetModel.id == pet_id).first()
        if not model:
            return None

        if data.nombre is not None:
            model.name = data.nombre
        if data.especie is not None:
            model.species = data.especie
        if data.raza is not None:
            model.breed = data.raza
        if data.edad is not None:
            pass  # edad se calcula desde fecha_nacimiento
        if data.peso is not None:
            model.weight = str(data.peso)
        if data.fecha_nacimiento is not None:
            dob = data.fecha_nacimiento
            if dob.tzinfo is None:
                dob = dob.replace(tzinfo=UTC)
            model.date_of_birth = dob

        self.db.flush()
        self.db.refresh(model)
        return self._to_domain(model)

    def delete_pet(self, pet_id: int) -> bool:
        """Eliminar una mascota (soft delete)."""
        model = self.db.query(PetModel).filter(PetModel.id == pet_id).first()
        if not model:
            return False

        model.is_active = False
        model.updated_at = datetime.now(UTC)
        self.db.flush()
        return True

    def get_pet_history(
        self,
        pet_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[PetHistoryEntry], int]:
        """Obtener historial basico de una mascota.

        El slice 007 no persiste aun registros de historial clinico, por lo
        que la implementacion devuelve una coleccion vacia con metadatos
        paginados consistentes.
        """
        _ = (pet_id, page, size)
        return [], 0
