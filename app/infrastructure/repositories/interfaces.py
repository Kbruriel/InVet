from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.user import User, UserCreate, UserUpdate, UserSession
from app.domain.value_objects import TokenData

class UserRepositoryInterface(ABC):
    """Interfaz para repositorio de usuarios"""
    
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def create_user(self, user_data: UserCreate) -> User:
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        pass

class SessionRepositoryInterface(ABC):
    """Interfaz para repositorio de sesiones"""
    
    @abstractmethod
    def create_session(self, session_data: UserSession) -> UserSession:
        pass
    
    @abstractmethod
    def get_by_token(self, token: str) -> Optional[UserSession]:
        pass
    
    @abstractmethod
    def delete_session(self, session_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_active_sessions_by_user(self, user_id: int) -> List[UserSession]:
        pass

class PasswordResetRepositoryInterface(ABC):
    """Interfaz para repositorio de tokens de restablecimiento"""
    
    @abstractmethod
    def create_reset_token(self, token_data: TokenData) -> str:
        pass
    
    @abstractmethod
    def get_reset_token(self, token: str) -> Optional[TokenData]:
        pass
    
    @abstractmethod
    def delete_reset_token(self, token: str) -> bool:
        pass