"""Modelo de clinica."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Clinic(Base):
    """Modelo de clinica para la base de datos."""

    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    owners = relationship(
        "Owner", lazy="noload", order_by="Owner.id", back_populates="clinic"
    )
    veterinarians = relationship(
        "Veterinarian",
        lazy="noload",
        order_by="Veterinarian.id",
        back_populates="clinic",
    )
