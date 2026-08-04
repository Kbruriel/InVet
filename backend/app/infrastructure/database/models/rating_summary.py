"""Modelo de resumen de calificaciones."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text

from app.infrastructure.database.models.base import Base


class RatingSummary(Base):
    """Modelo de resumen de calificaciones para la base de datos."""

    __tablename__ = "rating_summaries"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, unique=True)
    average_rating = Column(Float, nullable=False)
    total_reviews = Column(Integer, default=0)
    review_distribution = Column(Text)  # JSON string con distribución de calificaciones
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
