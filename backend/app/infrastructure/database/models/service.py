"""Modelo de servicio."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Float

from app.infrastructure.database.models.base import Base


class Service(Base):
    """Modelo de servicio para la base de datos."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer)  # En minutos
    price = Column(Float)  # Precio del servicio
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)