"""Implementacion concreta del repositorio de usuarios."""

from datetime import datetime
from typing import cast

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.domain.models import User, UserCreate, UserUpdate
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user import User as UserModel


class UserDatabaseRepository(UserRepository):
    """Implementacion del repositorio de usuarios con SQLAlchemy."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _to_domain(self, db_user: UserModel) -> User:
        return User(
            id=cast(int, db_user.id),
            email=cast(str, db_user.email),
            username=cast(str, db_user.username),
            hashed_password=cast(str, db_user.hashed_password),
            first_name=cast(str | None, db_user.first_name),
            last_name=cast(str | None, db_user.last_name),
            is_active=cast(bool, db_user.is_active),
            is_admin=cast(bool, db_user.is_admin),
            created_at=cast(datetime, db_user.created_at),
            updated_at=cast(datetime, db_user.updated_at),
        )

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Obtiene un usuario por ID."""
        db_user = (
            self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
        )
        return self._to_domain(db_user) if db_user else None

    async def get_user_by_email(self, email: str) -> User | None:
        """Obtiene un usuario por email."""
        db_user = (
            self.db_session.query(UserModel).filter(UserModel.email == email).first()
        )
        return self._to_domain(db_user) if db_user else None

    async def create_user(self, user_create: UserCreate) -> User:
        """Crea un nuevo usuario."""
        db_user = UserModel(
            email=user_create.email,
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password),
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            is_active=True,
            is_admin=False,
        )
        self.db_session.add(db_user)
        self.db_session.commit()
        self.db_session.refresh(db_user)
        return self._to_domain(db_user)

    async def update_user(self, user_id: int, user_update: UserUpdate) -> User | None:
        """Actualiza un usuario."""
        db_user = (
            self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
        )
        if not db_user:
            return None

        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)

        self.db_session.commit()
        self.db_session.refresh(db_user)
        return self._to_domain(db_user)

    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario."""
        db_user = (
            self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
        )
        if not db_user:
            return False

        self.db_session.delete(db_user)
        self.db_session.commit()
        return True

    async def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista usuarios con paginacion."""
        db_users = self.db_session.query(UserModel).offset(skip).limit(limit).all()
        return [self._to_domain(db_user) for db_user in db_users]
