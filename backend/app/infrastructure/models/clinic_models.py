"""SQLAlchemy models for branch-related clinic data."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.clinic import Clinic as ClinicDB
from app.infrastructure.database.session import Base


class BranchDB(Base):
    """Database model for branches."""

    __tablename__ = "branches"
    __table_args__ = {"extend_existing": True}

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

    clinic = relationship("Clinic", back_populates="branches")


class ServiceDB(Base):
    """Database model for services."""

    __tablename__ = "services"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration = Column(Integer)
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("BranchDB", back_populates="services")


class ScheduleDB(Base):
    """Database model for branch hours."""

    __tablename__ = "schedules"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    day_of_week = Column(Integer)
    open_time = Column(String(5))
    close_time = Column(String(5))
    is_closed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("BranchDB", back_populates="schedules")


class RatingDB(Base):
    """Database model for ratings."""

    __tablename__ = "ratings"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    user_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = relationship("BranchDB", back_populates="ratings")


ClinicDB.branches = relationship(
    "BranchDB", order_by=BranchDB.id, back_populates="clinic"
)
BranchDB.services = relationship(
    "ServiceDB", order_by=ServiceDB.id, back_populates="branch"
)
BranchDB.schedules = relationship(
    "ScheduleDB", order_by=ScheduleDB.id, back_populates="branch"
)
BranchDB.ratings = relationship(
    "RatingDB", order_by=RatingDB.id, back_populates="branch"
)
