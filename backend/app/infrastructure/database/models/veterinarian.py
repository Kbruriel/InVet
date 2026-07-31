"""Modelo de veterinario."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Veterinarian(Base):
    """Modelo de veterinario para la base de datos."""

    __tablename__ = "veterinarians"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    specialty = Column(String)
    license_number = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con sucursal
    branch = relationship("Branch", back_populates="veterinarians")


# Relación inversa en la tabla de sucursal
from app.infrastructure.database.models.branch import Branch

Branch.veterinarians = relationship(
    "Veterinarian", order_by=Veterinarian.id, back_populates="branch"
)