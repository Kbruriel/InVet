"""
Modelos SQLAlchemy para clínicas y sucursales
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base


class ClinicDB(Base):
    """Modelo de base de datos para Clínica"""
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    phone = Column(String(20))
    email = Column(String(255))
    lat = Column(Float)
    lng = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BranchDB(Base):
    """Modelo de base de datos para Sucursal"""
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    phone = Column(String(20))
    email = Column(String(255))
    lat = Column(Float)
    lng = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con clínica
    clinic = relationship("ClinicDB", back_populates="branches")


class ServiceDB(Base):
    """Modelo de base de datos para Servicio"""
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration = Column(Integer)  # en minutos
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con sucursal
    branch = relationship("BranchDB", back_populates="services")


class ScheduleDB(Base):
    """Modelo de base de datos para Horario"""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    day_of_week = Column(Integer)  # 0=Lunes, 6=Domingo
    open_time = Column(String(5))  # Formato HH:MM
    close_time = Column(String(5))  # Formato HH:MM
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con sucursal
    branch = relationship("BranchDB", back_populates="schedules")


class RatingDB(Base):
    """Modelo de base de datos para Calificación"""
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer)  # Puede ser NULL para usuarios anónimos
    rating = Column(Integer)  # De 1 a 5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con sucursal
    branch = relationship("BranchDB", back_populates="ratings")


# Relaciones de las tablas
ClinicDB.branches = relationship("BranchDB", order_by=BranchDB.id, back_populates="clinic")
BranchDB.services = relationship("ServiceDB", order_by=ServiceDB.id, back_populates="branch")
BranchDB.schedules = relationship("ScheduleDB", order_by=ScheduleDB.id, back_populates="branch")
BranchDB.ratings = relationship("RatingDB", order_by=RatingDB.id, back_populates="branch")