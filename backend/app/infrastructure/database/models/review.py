"""Modelos ORM para reseñas y respuestas clinicas (BE-012)."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Review(Base):
    """Reseña unica por cita completada."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(
        Integer,
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    branch_id = Column(
        Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    clinic_id = Column(
        Integer, ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("owners.id", ondelete="SET NULL"),
        nullable=True,
    )
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    response = relationship(
        "ReviewResponse",
        back_populates="review",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ReviewResponse(Base):
    """Respuesta clinica unica por reseña."""

    __tablename__ = "review_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(
        Integer,
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    branch_id = Column(
        Integer, ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("internal_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    review = relationship("Review", back_populates="response")
