"""
Interfaz de repositorio para Usuarios Internos
"""

from typing import List, Optional

from app.domain.entities.internal_user import (
    InternalUser,
    InternalUserCreate,
    InternalUserUpdate,
)


class InternalUserRepository:
    """Interfaz de repositorio para usuarios internos"""

    def create_internal_user(self, user: InternalUserCreate) -> InternalUser:
        raise NotImplementedError

    def get_internal_user(self, user_id: int) -> Optional[InternalUser]:
        raise NotImplementedError

    def get_internal_users(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[InternalUser]:
        raise NotImplementedError

    def update_internal_user(
        self, user_id: int, user_data: InternalUserUpdate
    ) -> Optional[InternalUser]:
        raise NotImplementedError

    def delete_internal_user(self, user_id: int) -> bool:
        raise NotImplementedError
