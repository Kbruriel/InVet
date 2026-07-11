"""Implementación del repositorio de usuarios internos."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.domain.entities.internal_user import (
    InternalUser,
    InternalUserCreate,
    InternalUserUpdate,
)
from app.domain.repositories.internal_user_repo import InternalUserRepository
from app.infrastructure.database.models.internal_user import (
    InternalUser as InternalUserDB,
)


class InternalUserRepositoryImpl(InternalUserRepository):
    """Implementación del repositorio de usuarios internos."""

    def __init__(self, db: Session):
        self.db = db

    def create_internal_user(self, user_data: InternalUserCreate) -> InternalUser:
        """Crea un nuevo usuario interno."""
        db_user = InternalUserDB(
            branch_id=user_data.branch_id,
            name=user_data.name,
            last_name=user_data.last_name,
            email=user_data.email,
            role=user_data.role,
            password_hash=get_password_hash(user_data.password),
            is_active=user_data.is_active,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._db_to_domain(db_user)

    def get_internal_user(self, user_id: int) -> Optional[InternalUser]:
        """Obtiene un usuario interno por ID."""
        db_user = (
            self.db.query(InternalUserDB).filter(InternalUserDB.id == user_id).first()
        )
        return self._db_to_domain(db_user) if db_user else None

    def get_internal_users(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[InternalUser]:
        """Obtiene una lista de usuarios internos para una sucursal."""
        db_users = (
            self.db.query(InternalUserDB)
            .filter(InternalUserDB.branch_id == branch_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._db_to_domain(db_user) for db_user in db_users]

    def update_internal_user(
        self, user_id: int, user_data: InternalUserUpdate
    ) -> Optional[InternalUser]:
        """Actualiza un usuario interno existente."""
        db_user = (
            self.db.query(InternalUserDB).filter(InternalUserDB.id == user_id).first()
        )
        if not db_user:
            return None

        updates = user_data.model_dump(exclude_unset=True)
        password = updates.pop("password", None)
        for key, value in updates.items():
            setattr(db_user, key, value)
        if password is not None:
            db_user.password_hash = get_password_hash(password)

        self.db.commit()
        self.db.refresh(db_user)
        return self._db_to_domain(db_user)

    def delete_internal_user(self, user_id: int) -> bool:
        """Elimina un usuario interno."""
        db_user = (
            self.db.query(InternalUserDB).filter(InternalUserDB.id == user_id).first()
        )
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    def _db_to_domain(self, db_user: InternalUserDB) -> InternalUser:
        """Convierte un modelo de base de datos a entidad de dominio."""
        return InternalUser(
            id=db_user.id,
            branch_id=db_user.branch_id,
            name=db_user.name,
            last_name=db_user.last_name,
            email=db_user.email,
            role=db_user.role,
            password_hash=db_user.password_hash,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
