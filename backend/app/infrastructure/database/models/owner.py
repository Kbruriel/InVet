"""Modelo de propietario."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Owner(Base):
    """Modelo de propietario para la base de datos."""

    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clinic_id = Column(Integer, ForeignKey("clinics.id"))
    clinic = relationship("Clinic", back_populates="owners")
    user = relationship("User", lazy="noload")
    pets = relationship("Pet", order_by="Pet.id", back_populates="owner")
