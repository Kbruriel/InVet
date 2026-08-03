from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.domain.user import User, UserCreate, UserUpdate, UserSession
from app.domain.value_objects import Token, TokenData, AuthCredentials, PasswordResetRequest, PasswordResetToken
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.session_repository import SessionRepository
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.exceptions import (
    InvalidCredentialsError, 
    UserNotFoundError, 
    TokenExpiredError,
    UserNotActiveError,
    PasswordResetTokenInvalidError
)

class AuthUseCase:
    """Caso de uso para operaciones de autenticación"""
    
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository):
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    def register_user(self, user_data: UserCreate) -> User:
        """Registrar un nuevo usuario"""
        # Verificar si el email ya está registrado
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise InvalidCredentialsError("Email already registered")
        
        # Hashear la contraseña
        hashed_password = get_password_hash(user_data.password)
        user_data_dict = user_data.dict()
        user_data_dict["hashed_password"] = hashed_password
        user_data_dict["created_at"] = datetime.utcnow()
        user_data_dict["updated_at"] = datetime.utcnow()
        
        return self.user_repo.create_user(User(**user_data_dict))
    
    def authenticate_user(self, credentials: AuthCredentials) -> Token:
        """Autenticar al usuario y crear tokens de acceso"""
        # Buscar el usuario por email
        user = self.user_repo.get_by_email(credentials.email)
        if not user:
            raise InvalidCredentialsError("Invalid credentials")
        
        # Verificar si el usuario está activo
        if not user.is_active:
            raise UserNotActiveError("User account is not active")
        
        # Verificar la contraseña
        if not verify_password(credentials.password, user.hashed_password):
            raise InvalidCredentialsError("Invalid credentials")
        
        # Generar token de acceso y refresh
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data=TokenData(
                user_id=user.id,
                email=user.email,
                role=user.role,
                token_type="access"
            ),
            expires_delta=access_token_expires
        )
        
        # Para ahora implementamos solo acceso, no refresh token real
        # En una implementación completa se crearía refresh_token = create_refresh_token(...)
        refresh_token = access_token  # placeholder temporal
        
        # Registrar sesion 
        session_data = {
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": datetime.utcnow() + refresh_token_expires,
            "created_at": datetime.utcnow()
        }
        self.session_repo.create_session(UserSession(**session_data))
        
        return Token(
            token=access_token,
            token_type="access",
            expires_at=datetime.utcnow() + access_token_expires,
            user_id=user.id
        )
    
    def refresh_access_token(self, refresh_token: str) -> Token:
        """Renovar el token de acceso usando el refresh token"""
        # Verificar si el refresh token existe y está activo
        session = self.session_repo.get_by_token(refresh_token)
        if not session or session.expires_at < datetime.utcnow():
            raise TokenExpiredError("Refresh token expired")
        
        # Obtener información del usuario
        user = self.user_repo.get_user_by_id(session.user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        # Generar nuevo access token (en una implementación real, aquí se haría 
        # una nueva generación de access token usando el refresh token)
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data=TokenData(
                user_id=user.id,
                email=user.email,
                role=user.role,
                token_type="access"
            ),
            expires_delta=access_token_expires
        )
        
        return Token(
            token=access_token,
            token_type="access",
            expires_at=datetime.utcnow() + access_token_expires,
            user_id=user.id
        )
    
    def logout_user(self, refresh_token: str) -> bool:
        """Cerrar la sesión de un usuario"""
        # Eliminar la sesión del refresh token
        session = self.session_repo.get_by_token(refresh_token)
        if session:
            self.session_repo.delete_session(session.id)
            return True
        return False
    
    def get_current_user(self, access_token: str) -> User:
        """Obtener información del usuario actual desde el token de acceso"""
        # Esta implementación sería para validar y usar el token JWT
        # En este momento solo devolverá un esqueleto, en una implementación real 
        # se implementaría validación real del token JWT
        raise NotImplementedError("JWT validation not implemented in this stub")
    
    def request_password_reset(self, email: str) -> bool:
        """Solicitar restablecimiento de contraseña"""
        # Buscar el usuario por email
        user = self.user_repo.get_by_email(email)
        if not user:
            return True  # No revelar si el email existe
        
        # Generar token de reset
        reset_token = create_refresh_token(
            data=TokenData(
                user_id=user.id,
                email=user.email,
                role=user.role,
                token_type="password_reset"
            ),
            expires_delta=timedelta(hours=1)  # Token válido por 1 hora
        )
        
        # Guardar el token (en un sistema real, se enviaría al usuario por email)
        reset_token_obj = PasswordResetToken(
            token=reset_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        
        # En esta implementación solo retornamos True como marca de éxito
        return True
    
    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Restablecer contraseña con token"""
        # Verificar que el token sea válido y activo
        token_data = self._validate_reset_token(reset_token)
        if not token_data:
            raise PasswordResetTokenInvalidError("Invalid or expired password reset token")
        
        # Actualizar la contraseña del usuario
        user = self.user_repo.get_user_by_id(token_data.user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        hashed_password = get_password_hash(new_password)
        user_update = UserUpdate(hashed_password=hashed_password)
        self.user_repo.update_user(user.id, user_update)
        
        # Eliminar el token de reset
        self._delete_reset_token(reset_token)
        
        return True
    
    def _validate_reset_token(self, reset_token: str) -> Optional[TokenData]:
        """Validar un token de restablecimiento de contraseña"""
        # Esta implementación es parcial - en una implementación real se validaría el token JWT
        raise NotImplementedError("JWT token validation not implemented in this stub")
    
    def _delete_reset_token(self, reset_token: str) -> None:
        """Eliminar un token de restablecimiento de contraseña"""
        # Implementación parcial - en una implementación real se eliminaría del almacén
        raise NotImplementedError("Reset token deletion not implemented in this stub")