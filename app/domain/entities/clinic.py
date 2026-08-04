from typing import List, Optional
from pydantic import BaseModel

class ScheduleItem(BaseModel):
    day_of_week: str
    open_time: str
    close_time: str

class ServiceItem(BaseModel):
    id: int
    name: str
    description: str
    duration_minutes: int

class RatingSummary(BaseModel):
    average_rating: float
    total_reviews: int

class BranchProfileResponse(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    email: str
    schedules: List[ScheduleItem]
    services: List[ServiceItem]
    rating_summary: RatingSummary
    is_available: bool

class ClinicProfileResponse(BaseModel):
    id: int
    clinic_name: str
    branch: BranchProfileResponse
    
class BranchCreateRequest(BaseModel):
    name: str
    address: str
    phone: str
    email: str
    schedules: List[ScheduleItem]
    services: List[ServiceItem]
    rating_summary: RatingSummary
    is_available: bool

class BranchUpdateRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    schedules: Optional[List[ScheduleItem]] = None
    services: Optional[List[ServiceItem]] = None
    rating_summary: Optional[RatingSummary] = None
    is_available: Optional[bool] = None

class BranchProfile(BaseModel):
    """Domain entity for branch profile data"""
    id: int
    name: str
    address: str
    phone: str
    email: str
    schedules: List[ScheduleItem]
    services: List[ServiceItem]
    rating_summary: RatingSummary
    is_available: bool