from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.auth import UserCreate, UserLogin, Token
from app.infrastructure.db import get_db
from app.application.auth_use_cases import AuthUseCase
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.session_repository import SessionRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        auth_use_case = AuthUseCase(user_repo, session_repo)
        
        # Registrar el usuario
        registered_user = auth_use_case.register_user(user)
        
        # Crear tokens de autenticación automáticamente
        token = auth_use_case.authenticate_user(UserLogin(email=user.email, password=user.password))
        
        return token
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión de usuario"""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        auth_use_case = AuthUseCase(user_repo, session_repo)
        
        # Autenticar al usuario y obtener tokens
        token = auth_use_case.authenticate_user(credentials)
        
        return token
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refrescar token de acceso"""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        auth_use_case = AuthUseCase(user_repo, session_repo)
        
        # Refrescar el token
        token = auth_use_case.refresh_access_token(refresh_token)
        
        return token
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout_user(refresh_token: str, db: Session = Depends(get_db)):
    """Cerrar sesión"""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        auth_use_case = AuthUseCase(user_repo, session_repo)
        
        # Cerrar sesión
        auth_use_case.logout_user(refresh_token)
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/password-reset-request")
async def request_password_reset(email: str, db: Session = Depends(get_db)):
    """Solicitar restablecimiento de contraseña"""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        auth_use_case = AuthUseCase(user_repo, session_repo)
        
        # Solicitar restablecimiento de contraseña
        auth_use_case.request_password_reset(email)
        
        return {"message": "If the email exists in our system, a reset link has been sent"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/password-reset")
async def reset_password(reset_token: str, new_password: str, db: Session = Depends(get_db)):
    """Restablecer contraseña"""
    try:
        user_repo = UserRepository(db)
        session_repo = SessionRepository(db)
        auth_use_case = AuthUseCase(user_repo, session_repo)
        
        # Restablecer contraseña
        auth_use_case.reset_password(reset_token, new_password)
        
        return {"message": "Password successfully reset"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))