"""Modelo de propietario."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database.models.base import Base


class Owner(Base):
    """Modelo de propietario para la base de datos."""
    
    __tablename__ = "owners"
    
    id = Column(Integer, primary_key=True, index=True)
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
    
    # Relación con clínica (opcional para la MVP)
    clinic_id = Column(Integer, ForeignKey("clinics.id"))
    
    # Relación con clínica
    clinic = relationship("Clinic", back_populates="owners")


# Relación inversa en la tabla de clínica
from app.infrastructure.database.models.clinic import Clinic

Clinic.owners = relationship("Owner", order_by=Owner.id, back_populates="clinic")