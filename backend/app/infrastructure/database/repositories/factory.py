"""Factory para instanciar repositorios (inyección de dependencias).

Este módulo centraliza toda la creación de repositorios para evitar que los
routers importen implementaciones concretas directamente.
"""

from sqlalchemy.orm import Session

from app.domain.repositories.owner_repository import OwnerRepository, PetRepository
from app.infrastructure.database.repositories.owner_repository_impl import (
    OwnerRepositoryImpl,
)
from app.infrastructure.database.repositories.pet_repository_impl import (
    PetRepositoryImpl,
)


def get_owner_repo(db: Session) -> OwnerRepository:
    """Obtener una instancia del repositorio de propietarios."""
    return OwnerRepositoryImpl(db)


def get_pet_repo(db: Session) -> PetRepository:
    """Obtener una instancia del repositorio de mascotas."""
    return PetRepositoryImpl(db)
