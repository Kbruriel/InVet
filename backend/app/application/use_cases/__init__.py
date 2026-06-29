"""
Casos de uso principales del sistema
"""
# Este archivo puede estar vacío inicialmente o contener importaciones
# de los casos de uso cuando se creen

from typing import Optional
from sqlalchemy.orm import Session
from app.domain.models import UserCreate, UserUpdate, UserResponse
from app.infrastructure.database.repositories import UserRepository


class UserUseCase:
    """Casos de uso relacionados con usuarios"""
    
    def __init__(self, db_session: Session):
        self.user_repo = UserRepository(db_session)
    
    def create_user(self, user_create: UserCreate) -> Optional[UserResponse]:
        """Crea un nuevo usuario"""
        # Aquí iría la lógica de negocio para crear un usuario
        # Por ahora solo se crea en el repositorio
        db_user = self.user_repo.create_user(user_create)
        if db_user:
            return UserResponse.from_orm(db_user)
        return None
    
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Obtiene un usuario por ID"""
        db_user = self.user_repo.get_user(user_id)
        if db_user:
            return UserResponse.from_orm(db_user)
        return None
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        """Actualiza un usuario existente"""
        db_user = self.user_repo.update_user(user_id, user_update)
        if db_user:
            return UserResponse.from_orm(db_user)
        return None