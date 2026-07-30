"""
Entidades del dominio para citas.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


# Estados de una cita
class AppointmentStatus(str, Enum):
    PENDING = "pending"  # Pendiente de confirmación
    CONFIRMED = "confirmed"  # Confirmada
    CANCELLED = "cancelled"  # Cancelada
    NO_SHOW = "no_show"  # No asistió
    COMPLETED = "completed"  # Completada


# Entidad de cita
class Appointment(BaseModel):
    id: int
    owner_id: int
    veterinarian_id: Optional[int] = None  # Puede ser opcional cuando aún no se asigna
    clinic_id: int
    branch_id: int
    appointment_slot_id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    scheduled_date: datetime  # Fecha y hora de la cita programada


# DTO para crear cita (sin ID ni estado)
class AppointmentCreate(BaseModel):
    owner_id: int
    veterinarian_id: Optional[int] = None
    clinic_id: int
    branch_id: int
    appointment_slot_id: int
    scheduled_date: datetime


# DTO para actualizar cita
class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    veterinarian_id: Optional[int] = None


# DTO para respuesta de cita
class AppointmentResponse(Appointment):
    pass


# Entidad de franja horaria disponible
class AppointmentSlot(BaseModel):
    id: int
    clinic_id: int
    branch_id: int
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    created_at: datetime
    updated_at: datetime


# DTO para crear franja horaria
class AppointmentSlotCreate(BaseModel):
    clinic_id: int
    branch_id: int
    start_time: datetime
    end_time: datetime
    is_available: bool = True


# DTO para respuesta de franja horaria
class AppointmentSlotResponse(AppointmentSlot):
    pass
