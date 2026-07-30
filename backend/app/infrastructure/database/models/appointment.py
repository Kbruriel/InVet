"""
Modelos SQLAlchemy para citas
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False)
    veterinarian_id = Column(Integer, nullable=True)
    clinic_id = Column(Integer, nullable=False)
    branch_id = Column(Integer, nullable=False)
    appointment_slot_id = Column(
        Integer, ForeignKey("appointment_slots.id"), nullable=False
    )
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    scheduled_date = Column(DateTime, nullable=False)

    # Relación con la franja horaria
    slot = relationship("AppointmentSlot", back_populates="appointments")


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, nullable=False)
    branch_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relación inversa con citas
    appointments = relationship("Appointment", back_populates="slot")

    # Índices para mejorar la consulta de franjas disponibles por clínica y sucursal
    __table_args__ = (
        Index("idx_clinic_branch_available", "clinic_id", "branch_id", "is_available"),
    )
