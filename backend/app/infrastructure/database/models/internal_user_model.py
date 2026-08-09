"""Modelo ORM de usuario interno."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class InternalUser(Base):
    """Modelo de usuario interno para la base de datos."""

    __tablename__ = "internal_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    rol = Column(String(50), nullable=False)
    branch_ids = Column(Text)  # JSON string of branch IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    clinic = relationship("Clinic", lazy="noload")

    def __repr__(self) -> str:
        return f"<InternalUser(id={self.id}, nombre={self.nombre!r})>"
