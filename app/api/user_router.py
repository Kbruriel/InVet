from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.auth import UserPublic
from app.infrastructure.db import get_db

router = APIRouter(prefix="/me", tags=["User Profile"])

@router.get("/", response_model=UserPublic)
async def get_current_user(db: Session = Depends(get_db)):
    """Obtener información del usuario actual (se debería implementar con JWT)"""
    # En una implementación real, esta ruta usaría el token JWT para identificar 
    # al usuario actual y devolver su información
    raise HTTPException(status_code=501, detail="Endpoint not implemented yet")