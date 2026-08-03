from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.domain.user import UserSession
from app.infrastructure.repositories.interfaces import SessionRepositoryInterface
from app.infrastructure.models.session import UserSession as SessionModel

class SessionRepository(SessionRepositoryInterface):
    """Repositorio concreto de sesiones usando SQLAlchemy"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_session(self, session_data: UserSession) -> UserSession:
        """Crear nueva sesión"""
        db_session = SessionModel(**session_data.dict())
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return UserSession.from_orm(db_session)
    
    def get_by_token(self, token: str) -> Optional[UserSession]:
        """Obtener sesión por token"""
        db_session = self.db.query(SessionModel).filter(SessionModel.token == token).first()
        return UserSession.from_orm(db_session) if db_session else None
    
    def delete_session(self, session_id: int) -> bool:
        """Eliminar sesión por ID"""
        db_session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not db_session:
            return False
        
        self.db.delete(db_session)
        self.db.commit()
        return True
    
    def get_active_sessions_by_user(self, user_id: int) -> List[UserSession]:
        """Obtener todas las sesiones activas para un usuario"""
        db_sessions = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.expires_at > datetime.utcnow()
        ).all()
        
        return [UserSession.from_orm(db_session) for db_session in db_sessions]