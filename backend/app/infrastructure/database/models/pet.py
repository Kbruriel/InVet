"""Modelo de mascota."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Pet(Base):
    """Modelo de mascota para la base de datos."""

    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("owners.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    breed = Column(String)
    color = Column(String)
    gender = Column(String)  # 'male', 'female'
    weight = Column(String)
    date_of_birth = Column(DateTime)
    has_medical_history = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    owner = relationship("Owner", back_populates="pets")


# Relación inversa en la tabla de propietario
from app.infrastructure.database.models.owner import Owner

Owner.pets = relationship("Pet", order_by=Pet.id, back_populates="owner")
