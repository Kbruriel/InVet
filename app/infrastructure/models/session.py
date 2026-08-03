from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from app.infrastructure.models.base import Base

class UserSession(Base):
    """Modelo SQLAlchemy para sesiones de usuarios"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)