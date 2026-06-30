"""
Value Objects para horarios
"""
from datetime import time
from typing import List, Optional
from pydantic import BaseModel


class WorkingHours(BaseModel):
    """Horario de trabajo - value object"""
    day_of_week: int  # 0=Lunes, 6=Domingo
    open_time: time
    close_time: time
    is_closed: bool = False


class ScheduleAvailability(BaseModel):
    """Disponibilidad del horario"""
    date: str  # Formato YYYY-MM-DD
    available_slots: List[str]  # Formato HH:MM