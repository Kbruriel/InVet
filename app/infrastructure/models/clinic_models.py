from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ClinicBranch(Base):
    __tablename__ = "clinic_branches"
    
    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    
    # Relationship to schedules
    schedules = relationship("BranchSchedule", back_populates="branch")
    services = relationship("BranchService", back_populates="branch")
    
class BranchSchedule(Base):
    __tablename__ = "branch_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, nullable=False)
    day_of_week = Column(String, nullable=False)
    open_time = Column(String, nullable=False)  # Format HH:MM
    close_time = Column(String, nullable=False)  # Format HH:MM
    
    branch = relationship("ClinicBranch", back_populates="schedules")

class BranchService(Base):
    __tablename__ = "branch_services"
    
    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    
    branch = relationship("ClinicBranch", back_populates="services")