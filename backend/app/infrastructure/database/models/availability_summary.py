"""Modelo de resumen de disponibilidad."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, String
from app.infrastructure.database.models.base import Base


class AvailabilitySummary(Base):
    """Modelo de resumen de disponibilidad para la base de datos."""
    
    __tablename__ = "availability_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, unique=True)
    is_available = Column(Boolean, default=True)
    next_available_time = Column(DateTime)  # Próxima hora disponible
    availability_type = Column(String(50))  # "full", "limited", "closed"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)