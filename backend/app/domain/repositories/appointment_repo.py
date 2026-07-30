"""
Interfaces de repositorios del dominio para citas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentSlot,
    AppointmentSlotCreate,
)


class AppointmentRepository(ABC):
    """Interface for appointment repository"""

    @abstractmethod
    def create(self, appointment: AppointmentCreate) -> Appointment:
        pass

    @abstractmethod
    def find_by_id(self, appointment_id: int) -> Optional[Appointment]:
        pass

    @abstractmethod
    def find_by_owner_id(self, owner_id: int) -> List[Appointment]:
        pass

    @abstractmethod
    def update_status(self, appointment_id: int, status: str) -> Optional[Appointment]:
        pass

    @abstractmethod
    def cancel(self, appointment_id: int) -> Optional[Appointment]:
        pass

    @abstractmethod
    def confirm(self, appointment_id: int) -> Optional[Appointment]:
        pass

    @abstractmethod
    def reschedule(
        self, appointment_id: int, new_slot_id: int
    ) -> Optional[Appointment]:
        pass

    @abstractmethod
    def mark_no_show(self, appointment_id: int) -> Optional[Appointment]:
        pass

    @abstractmethod
    def complete(self, appointment_id: int) -> Optional[Appointment]:
        pass


class AppointmentSlotRepository(ABC):
    """Interface for appointment slot repository"""

    @abstractmethod
    def find_available_slots_by_clinic_branch(
        self, clinic_id: int, branch_id: int
    ) -> List[AppointmentSlot]:
        pass

    @abstractmethod
    def create(self, slot: AppointmentSlotCreate) -> AppointmentSlot:
        pass

    @abstractmethod
    def find_by_id(self, slot_id: int) -> Optional[AppointmentSlot]:
        pass

    @abstractmethod
    def is_slot_available(self, slot_id: int) -> bool:
        pass

    @abstractmethod
    def mark_available(self, slot_id: int) -> Optional[AppointmentSlot]:
        pass

    @abstractmethod
    def mark_unavailable(self, slot_id: int) -> Optional[AppointmentSlot]:
        pass
