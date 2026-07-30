"""
Repositorios SQLAlchemy para citas.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentSlot,
    AppointmentSlotCreate,
)
from app.domain.repositories.appointment_repo import (
    AppointmentRepository,
    AppointmentSlotRepository,
)
from app.infrastructure.database.models.appointment import Appointment as AppointmentDB
from app.infrastructure.database.models.appointment import (
    AppointmentSlot as AppointmentSlotDB,
)


class AppointmentRepositoryImpl(AppointmentRepository):
    """Implementación del repositorio de citas"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, appointment: AppointmentCreate) -> Appointment:
        db_appointment = AppointmentDB(
            owner_id=appointment.owner_id,
            veterinarian_id=appointment.veterinarian_id,
            clinic_id=appointment.clinic_id,
            branch_id=appointment.branch_id,
            appointment_slot_id=appointment.appointment_slot_id,
            status="pending",
            scheduled_date=appointment.scheduled_date,
        )
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)

        return Appointment(
            id=db_appointment.id,
            owner_id=db_appointment.owner_id,
            veterinarian_id=db_appointment.veterinarian_id,
            clinic_id=db_appointment.clinic_id,
            branch_id=db_appointment.branch_id,
            appointment_slot_id=db_appointment.appointment_slot_id,
            status=db_appointment.status,
            created_at=db_appointment.created_at,
            updated_at=db_appointment.updated_at,
            scheduled_date=db_appointment.scheduled_date,
        )

    def find_by_id(self, appointment_id: int) -> Optional[Appointment]:
        db_appointment = (
            self.db.query(AppointmentDB)
            .filter(AppointmentDB.id == appointment_id)
            .first()
        )
        if not db_appointment:
            return None

        return Appointment(
            id=db_appointment.id,
            owner_id=db_appointment.owner_id,
            veterinarian_id=db_appointment.veterinarian_id,
            clinic_id=db_appointment.clinic_id,
            branch_id=db_appointment.branch_id,
            appointment_slot_id=db_appointment.appointment_slot_id,
            status=db_appointment.status,
            created_at=db_appointment.created_at,
            updated_at=db_appointment.updated_at,
            scheduled_date=db_appointment.scheduled_date,
        )

    def find_by_owner_id(self, owner_id: int) -> List[Appointment]:
        db_appointments = (
            self.db.query(AppointmentDB)
            .filter(AppointmentDB.owner_id == owner_id)
            .all()
        )
        return [
            Appointment(
                id=db_appointment.id,
                owner_id=db_appointment.owner_id,
                veterinarian_id=db_appointment.veterinarian_id,
                clinic_id=db_appointment.clinic_id,
                branch_id=db_appointment.branch_id,
                appointment_slot_id=db_appointment.appointment_slot_id,
                status=db_appointment.status,
                created_at=db_appointment.created_at,
                updated_at=db_appointment.updated_at,
                scheduled_date=db_appointment.scheduled_date,
            )
            for db_appointment in db_appointments
        ]

    def update_status(self, appointment_id: int, status: str) -> Optional[Appointment]:
        db_appointment = (
            self.db.query(AppointmentDB)
            .filter(AppointmentDB.id == appointment_id)
            .first()
        )
        if not db_appointment:
            return None

        db_appointment.status = status
        db_appointment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_appointment)

        return Appointment(
            id=db_appointment.id,
            owner_id=db_appointment.owner_id,
            veterinarian_id=db_appointment.veterinarian_id,
            clinic_id=db_appointment.clinic_id,
            branch_id=db_appointment.branch_id,
            appointment_slot_id=db_appointment.appointment_slot_id,
            status=db_appointment.status,
            created_at=db_appointment.created_at,
            updated_at=db_appointment.updated_at,
            scheduled_date=db_appointment.scheduled_date,
        )

    def cancel(self, appointment_id: int) -> Optional[Appointment]:
        return self.update_status(appointment_id, "cancelled")

    def confirm(self, appointment_id: int) -> Optional[Appointment]:
        return self.update_status(appointment_id, "confirmed")

    def reschedule(
        self, appointment_id: int, new_slot_id: int
    ) -> Optional[Appointment]:
        db_appointment = (
            self.db.query(AppointmentDB)
            .filter(AppointmentDB.id == appointment_id)
            .first()
        )
        if not db_appointment:
            return None

        db_appointment.appointment_slot_id = new_slot_id
        db_appointment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_appointment)

        return Appointment(
            id=db_appointment.id,
            owner_id=db_appointment.owner_id,
            veterinarian_id=db_appointment.veterinarian_id,
            clinic_id=db_appointment.clinic_id,
            branch_id=db_appointment.branch_id,
            appointment_slot_id=db_appointment.appointment_slot_id,
            status=db_appointment.status,
            created_at=db_appointment.created_at,
            updated_at=db_appointment.updated_at,
            scheduled_date=db_appointment.scheduled_date,
        )

    def mark_no_show(self, appointment_id: int) -> Optional[Appointment]:
        return self.update_status(appointment_id, "no_show")

    def complete(self, appointment_id: int) -> Optional[Appointment]:
        return self.update_status(appointment_id, "completed")


class AppointmentSlotRepositoryImpl(AppointmentSlotRepository):
    """Implementación del repositorio de franjas horarias"""

    def __init__(self, db: Session):
        self.db = db

    def find_available_slots_by_clinic_branch(
        self, clinic_id: int, branch_id: int
    ) -> List[AppointmentSlot]:
        db_slots = (
            self.db.query(AppointmentSlotDB)
            .filter(
                AppointmentSlotDB.clinic_id == clinic_id,
                AppointmentSlotDB.branch_id == branch_id,
                AppointmentSlotDB.is_available == True,
            )
            .all()
        )

        return [
            AppointmentSlot(
                id=db_slot.id,
                clinic_id=db_slot.clinic_id,
                branch_id=db_slot.branch_id,
                start_time=db_slot.start_time,
                end_time=db_slot.end_time,
                is_available=db_slot.is_available,
                created_at=db_slot.created_at,
                updated_at=db_slot.updated_at,
            )
            for db_slot in db_slots
        ]

    def create(self, slot: AppointmentSlotCreate) -> AppointmentSlot:
        db_slot = AppointmentSlotDB(
            clinic_id=slot.clinic_id,
            branch_id=slot.branch_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            is_available=slot.is_available,
        )
        self.db.add(db_slot)
        self.db.commit()
        self.db.refresh(db_slot)

        return AppointmentSlot(
            id=db_slot.id,
            clinic_id=db_slot.clinic_id,
            branch_id=db_slot.branch_id,
            start_time=db_slot.start_time,
            end_time=db_slot.end_time,
            is_available=db_slot.is_available,
            created_at=db_slot.created_at,
            updated_at=db_slot.updated_at,
        )

    def find_by_id(self, slot_id: int) -> Optional[AppointmentSlot]:
        db_slot = (
            self.db.query(AppointmentSlotDB)
            .filter(AppointmentSlotDB.id == slot_id)
            .first()
        )
        if not db_slot:
            return None

        return AppointmentSlot(
            id=db_slot.id,
            clinic_id=db_slot.clinic_id,
            branch_id=db_slot.branch_id,
            start_time=db_slot.start_time,
            end_time=db_slot.end_time,
            is_available=db_slot.is_available,
            created_at=db_slot.created_at,
            updated_at=db_slot.updated_at,
        )

    def is_slot_available(self, slot_id: int) -> bool:
        db_slot = (
            self.db.query(AppointmentSlotDB)
            .filter(AppointmentSlotDB.id == slot_id)
            .first()
        )
        return db_slot is not None and db_slot.is_available

    def _set_slot_availability(
        self, slot_id: int, is_available: bool
    ) -> Optional[AppointmentSlot]:
        db_slot = (
            self.db.query(AppointmentSlotDB)
            .filter(AppointmentSlotDB.id == slot_id)
            .first()
        )
        if not db_slot:
            return None

        db_slot.is_available = is_available
        db_slot.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_slot)

        return AppointmentSlot(
            id=db_slot.id,
            clinic_id=db_slot.clinic_id,
            branch_id=db_slot.branch_id,
            start_time=db_slot.start_time,
            end_time=db_slot.end_time,
            is_available=db_slot.is_available,
            created_at=db_slot.created_at,
            updated_at=db_slot.updated_at,
        )

    def mark_available(self, slot_id: int) -> Optional[AppointmentSlot]:
        return self._set_slot_availability(slot_id, True)

    def mark_unavailable(self, slot_id: int) -> Optional[AppointmentSlot]:
        return self._set_slot_availability(slot_id, False)
