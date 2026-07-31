"""
Casos de uso para Usuarios Internos
"""
from typing import List, Optional

from app.domain.entities.internal_user import InternalUser, InternalUserCreate, InternalUserUpdate
from app.domain.repositories.internal_user_repo import InternalUserRepository


class InternalUserUseCase:
    """Casos de uso para gestión de usuarios internos"""
    
    def __init__(self, internal_user_repository: InternalUserRepository):
        self.internal_user_repository = internal_user_repository
    
    def create_internal_user(self, user_data: InternalUserCreate) -> InternalUser:
        """Crea un nuevo usuario interno"""
        return self.internal_user_repository.create_internal_user(user_data)
    
    def get_internal_user(self, user_id: int) -> Optional[InternalUser]:
        """Obtiene un usuario interno por ID"""
        return self.internal_user_repository.get_internal_user(user_id)
    
    def get_internal_users(self, branch_id: int, skip: int = 0, limit: int = 100) -> List[InternalUser]:
        """Obtiene una lista de usuarios internos para una sucursal"""
        return self.internal_user_repository.get_internal_users(branch_id, skip, limit)
    
    def update_internal_user(self, user_id: int, user_data: InternalUserUpdate) -> Optional[InternalUser]:
        """Actualiza un usuario interno existente"""
        return self.internal_user_repository.update_internal_user(user_id, user_data)
    
    def delete_internal_user(self, user_id: int) -> bool:
        """Elimina un usuario interno"""
        return self.internal_user_repository.delete_internal_user(user_id)