"""Modelo de horario de sucursal."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Time

from app.infrastructure.database.models.base import Base


class BranchSchedule(Base):
    """Modelo de horario de sucursal para la base de datos."""

    __tablename__ = "branch_schedules"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=domingo, 1=lunes, ..., 6=sábado
    open_time = Column(Time, nullable=False)
    close_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
