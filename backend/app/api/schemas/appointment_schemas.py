"""
Schemas Pydantic para las citas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Schemas de entrada (request)
class AppointmentCreateRequest(BaseModel):
    owner_id: int
    veterinarian_id: Optional[int] = None
    clinic_id: int
    branch_id: int
    appointment_slot_id: int
    scheduled_date: datetime

class AppointmentUpdateRequest(BaseModel):
    status: Optional[str] = None
    veterinarian_id: Optional[int] = None

class AppointmentSlotCreateRequest(BaseModel):
    clinic_id: int
    branch_id: int
    start_time: datetime
    end_time: datetime
    is_available: bool = True

# Schemas de salida (response)
class AppointmentResponse(BaseModel):
    id: int
    owner_id: int
    veterinarian_id: Optional[int] = None
    clinic_id: int
    branch_id: int
    appointment_slot_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    scheduled_date: datetime

class AppointmentSlotResponse(BaseModel):
    id: int
    clinic_id: int
    branch_id: int
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    created_at: datetime
    updated_at: datetime

# Schema de respuesta para listados
class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    total: int
    page: int
    per_page: int