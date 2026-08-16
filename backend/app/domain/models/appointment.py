"""Appointment domain model and AppointmentStatus enum."""

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AppointmentStatus(str, Enum):
    """Valid states for an appointment with transition rules."""

    PENDING = "pending"
    APPROVED = "approved"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

    @property
    def is_terminal(self) -> bool:
        """Return True if this status cannot be transitioned from."""
        return self in (self.COMPLETED, self.NO_SHOW, self.CANCELLED)

    def can_transition_to(self, target: "AppointmentStatus") -> bool:
        """Check whether a transition from current to target is allowed."""
        transitions = {
            self.PENDING: {self.APPROVED, self.CANCELLED, self.RESCHEDULED},
            self.APPROVED: {self.CONFIRMED, self.CANCELLED, self.RESCHEDULED},
            self.CONFIRMED: {self.COMPLETED, self.NO_SHOW, self.CANCELLED},
            self.RESCHEDULED: {self.PENDING, self.CANCELLED},
        }
        allowed = transitions.get(self, set())
        return target in allowed


class AppointmentType(str, Enum):
    """Types of veterinary appointments."""

    CONSULTA_GENERAL = "consulta_general"
    VACUNACION = "vacunacion"
    CONTROL = "control"
    REEMERGENCIA = "reemergencia"


# ---- Domain Model ----


class Appointment(BaseModel):
    """Domain representation of an appointment."""

    id: Optional[int] = None
    owner_id: int
    pet_id: int
    veterinarian_id: Optional[int] = None
    clinic_id: int
    branch_id: int
    appointment_type: AppointmentType
    status: AppointmentStatus = AppointmentStatus.PENDING
    scheduled_start: datetime
    scheduled_end: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_by: int

    @field_validator("scheduled_end")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        if hasattr(info, "data") and info.data.get("scheduled_start"):
            if v <= info.data["scheduled_start"]:
                raise ValueError("scheduled_end must be after scheduled_start")
        return v


# ---- Pydantic Schemas for API ----


class AppointmentCreateSchema(BaseModel):
    """Schema for creating an appointment."""

    pet_id: int = Field(..., gt=0)
    veterinarian_id: Optional[int] = None
    clinic_id: int = Field(..., gt=0)
    branch_id: int = Field(..., gt=0)
    appointment_type: AppointmentType
    scheduled_start: datetime = Field(..., description="Must be in the future")
    scheduled_end: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason: Optional[str] = None

    @field_validator("scheduled_start")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        if v.date() <= date.today():
            raise ValueError("scheduled_start must be in the future")
        return v

    @field_validator("scheduled_end")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        if hasattr(info, "data") and info.data.get("scheduled_start"):
            if v <= info.data["scheduled_start"]:
                raise ValueError("scheduled_end must be after scheduled_start")
        return v


class AppointmentUpdateSchema(BaseModel):
    """Schema for updating appointment status."""

    action: str = Field(..., description="approve|confirm|complete|cancel|no_show|reschedule")
    new_start: Optional[datetime] = None
    new_end: Optional[datetime] = None
    reason: Optional[str] = None


class AppointmentRescheduleSchema(BaseModel):
    """Schema for rescheduling an appointment."""

    new_start: datetime = Field(..., description="Must be in the future")
    new_end: datetime
    reason: Optional[str] = None

    @field_validator("new_start")
    @classmethod
    def validate_future(cls, v: datetime) -> datetime:
        if v.date() <= date.today():
            raise ValueError("new_start must be in the future")
        return v


class SlotSchema(BaseModel):
    """Availability slot response."""

    start: datetime
    end: datetime
    available: bool = True


class AvailabilityResponse(BaseModel):
    """Response for availability endpoint."""

    slots: list[SlotSchema]
