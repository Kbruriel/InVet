"""Pydantic schemas for clinic and branch endpoints."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""

    skip: int
    limit: int
    total: int


class BranchProfileResponse(BaseModel):
    """Public branch profile response."""

    branch: Dict[str, Any]
    services: List[Dict[str, Any]]
    schedules: List[Dict[str, Any]]
    ratings_summary: Dict[str, Any]


class ScheduleResponse(BaseModel):
    """Public schedule response."""

    id: int
    branch_id: int
    day_of_week: int
    open_time: str
    close_time: str
    is_closed: bool
    created_at: datetime
    updated_at: datetime


class ServiceResponse(BaseModel):
    """Service response."""

    id: int
    branch_id: int
    name: str
    description: Optional[str] = None
    duration: int
    price: float
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RatingSummaryResponse(BaseModel):
    """Rating summary response."""

    average_rating: float
    total_ratings: int
    rating_distribution: Dict[int, int]


class BranchPublicDataResponse(BaseModel):
    """Basic public branch data."""

    id: int
    clinic_id: int
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClinicBase(BaseModel):
    """Shared clinic administration fields."""

    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class ClinicCreate(ClinicBase):
    """Payload for clinic creation."""


class ClinicUpdate(BaseModel):
    """Payload for clinic updates."""

    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_active: Optional[bool] = None


class ClinicRead(ClinicBase):
    """Clinic response for administration endpoints."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedClinicsResponse(BaseModel):
    """Paginated clinic list."""

    items: List[ClinicRead]
    pagination: PaginationMeta


class BranchBase(BaseModel):
    """Shared branch administration fields."""

    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class BranchCreate(BranchBase):
    """Payload for branch creation."""

    clinic_id: int


class BranchUpdate(BaseModel):
    """Payload for branch updates."""

    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_active: Optional[bool] = None


class BranchRead(BranchBase):
    """Branch response for administration endpoints."""

    id: int
    clinic_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PaginatedBranchesResponse(BaseModel):
    """Paginated branch list."""

    items: List[BranchRead]
    pagination: PaginationMeta


class ScheduleCreate(BaseModel):
    """Payload for creating branch hours."""

    day_of_week: int = Field(ge=0, le=6)
    open_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    close_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    is_closed: bool = False


class ScheduleUpdate(BaseModel):
    """Payload for updating branch hours."""

    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    open_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    close_time: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    is_closed: Optional[bool] = None


class ScheduleAdminRead(BaseModel):
    """Schedule response for administration endpoints."""

    id: int
    branch_id: int
    day_of_week: int
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    is_closed: bool
    created_at: datetime
    updated_at: datetime
