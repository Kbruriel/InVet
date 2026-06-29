"""Implementación concreta del repositorio de usuarios."""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.models import User, UserCreate, UserUpdate
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.base import Base
from app.infrastructure.database.models.user import User as UserModel


class UserDatabaseRepository(UserRepository):
    """Implementación del repositorio de usuarios con SQLAlchemy."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene un usuario por ID."""
        db_user = self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return User(
                id=db_user.id,
                email=db_user.email,
                username=db_user.username,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_admin=db_user.is_admin,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por email."""
        db_user = self.db_session.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return User(
                id=db_user.id,
                email=db_user.email,
                username=db_user.username,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_admin=db_user.is_admin,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
        return None
    
    async def create_user(self, user_create: UserCreate) -> User:
        """Crea un nuevo usuario."""
        db_user = UserModel(
            email=user_create.email,
            username=user_create.username,
            hashed_password=user_create.password,  # En un caso real se debería hashear
            is_active=True,
            is_admin=False
        )
        self.db_session.add(db_user)
        self.db_session.commit()
        self.db_session.refresh(db_user)
        
        return User(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Actualiza un usuario."""
        db_user = self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None
        
        # Actualizar los campos proporcionados
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        
        self.db_session.commit()
        self.db_session.refresh(db_user)
        
        return User(
            id=db_user.id,
            email=db_user.email,
            username=db_user.username,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_admin=db_user.is_admin,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    async def delete_user(self, user_id: int) -> bool:
        """Elimina un usuario."""
        db_user = self.db_session.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        
        self.db_session.delete(db_user)
        self.db_session.commit()
        return True
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Lista usuarios con paginación."""
        db_users = self.db_session.query(UserModel).offset(skip).limit(limit).all()
        return [
            User(
                id=db_user.id,
                email=db_user.email,
                username=db_user.username,
                hashed_password=db_user.hashed_password,
                is_active=db_user.is_active,
                is_admin=db_user.is_admin,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )
            for db_user in db_users
        ]