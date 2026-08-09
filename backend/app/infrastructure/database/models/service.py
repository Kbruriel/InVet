"""Modelo ORM de servicio para slice 006."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Service(Base):
    """Modelo de servicio para la base de datos (slice 006)."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column("price", Integer, nullable=False)  # Stored as cents to avoid float issues
    duration_minutes = Column("duration_minutes", Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    clinic = relationship("Clinic", lazy="noload")

    __table_args__ = (
        UniqueConstraint("clinic_id", "name", name="uq_service_clinic_name"),
    )

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, name={self.name!r})>"
