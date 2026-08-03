from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.user import User, UserCreate, UserUpdate
from app.infrastructure.repositories.interfaces import UserRepositoryInterface
from app.infrastructure.models.user import User as UserModel

class UserRepository(UserRepositoryInterface):
    """Repositorio concreto de usuarios usando SQLAlchemy"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return User.from_orm(db_user) if db_user else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return User.from_orm(db_user) if db_user else None
    
    def create_user(self, user_data: UserCreate) -> User:
        """Crear nuevo usuario"""
        db_user = UserModel(**user_data.dict(exclude={"password"}))
        db_user.hashed_password = user_data.password  # Aquí debería ser hasheada
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User.from_orm(db_user)
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """Actualizar usuario"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            raise Exception("User not found")  # Esto debería ser una excepción específica
        
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return User.from_orm(db_user)

    def delete_user(self, user_id: int) -> bool:
        """Eliminar usuario"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True