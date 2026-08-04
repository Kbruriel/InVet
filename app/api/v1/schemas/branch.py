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

class BranchPublicProfile(BaseModel):
    """Schema for public branch profile data"""
    id: int
    name: str
    address: str
    phone: str
    email: str
    schedules: List[ScheduleItem]
    services: List[ServiceItem]
    rating_summary: RatingSummary
    is_available: bool

class BranchProfileResponse(BaseModel):
    """Complete profile response schema including clinic info"""
    id: int
    clinic_id: int
    name: str
    address: str
    phone: str
    email: str
    schedules: List[ScheduleItem]
    services: List[ServiceItem]
    rating_summary: RatingSummary
    is_available: bool
