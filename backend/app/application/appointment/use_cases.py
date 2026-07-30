"""
Casos de uso para la gestion de citas.
"""

from typing import List, Optional

from app.domain.entities.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentSlot,
    AppointmentStatus,
)
from app.domain.repositories.appointment_repo import (
    AppointmentRepository,
    AppointmentSlotRepository,
)


class CreateAppointmentUseCase:
    """Caso de uso para crear una cita."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        slot_repo: AppointmentSlotRepository,
    ):
        self.appointment_repo = appointment_repo
        self.slot_repo = slot_repo

    def execute(self, appointment_data: AppointmentCreate) -> Appointment:
        slot = self.slot_repo.find_by_id(appointment_data.appointment_slot_id)
        if not slot or not slot.is_available:
            raise ValueError("La franja horaria no esta disponible")

        reserved_slot = self.slot_repo.mark_unavailable(slot.id)
        if not reserved_slot:
            raise ValueError("No se pudo reservar la franja horaria")

        try:
            return self.appointment_repo.create(appointment_data)
        except Exception:
            self.slot_repo.mark_available(slot.id)
            raise


class ConfirmAppointmentUseCase:
    """Caso de uso para confirmar una cita."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
    ):
        self.appointment_repo = appointment_repo

    def execute(self, appointment_id: int) -> Optional[Appointment]:
        appointment = self.appointment_repo.find_by_id(appointment_id)
        if not appointment:
            return None

        if appointment.status != AppointmentStatus.PENDING:
            raise ValueError("Solo se puede confirmar citas pendientes")

        return self.appointment_repo.confirm(appointment_id)


class CancelAppointmentUseCase:
    """Caso de uso para cancelar una cita."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        slot_repo: AppointmentSlotRepository,
    ):
        self.appointment_repo = appointment_repo
        self.slot_repo = slot_repo

    def execute(self, appointment_id: int) -> Optional[Appointment]:
        appointment = self.appointment_repo.find_by_id(appointment_id)
        if not appointment:
            return None

        if appointment.status not in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ]:
            raise ValueError("Solo se pueden cancelar citas pendientes o confirmadas")

        cancelled = self.appointment_repo.cancel(appointment_id)
        if cancelled:
            self.slot_repo.mark_available(appointment.appointment_slot_id)
        return cancelled


class RescheduleAppointmentUseCase:
    """Caso de uso para reprogramar una cita."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        slot_repo: AppointmentSlotRepository,
    ):
        self.appointment_repo = appointment_repo
        self.slot_repo = slot_repo

    def execute(self, appointment_id: int, new_slot_id: int) -> Optional[Appointment]:
        appointment = self.appointment_repo.find_by_id(appointment_id)
        if not appointment:
            return None

        new_slot = self.slot_repo.find_by_id(new_slot_id)
        if not new_slot or not new_slot.is_available:
            raise ValueError("La nueva franja horaria no esta disponible")

        if appointment.appointment_slot_id == new_slot_id:
            raise ValueError("La nueva fecha debe ser diferente de la actual")

        reserved_slot = self.slot_repo.mark_unavailable(new_slot_id)
        if not reserved_slot:
            raise ValueError("No se pudo reservar la nueva franja horaria")

        try:
            updated_appointment = self.appointment_repo.reschedule(
                appointment_id, new_slot_id
            )
            if not updated_appointment:
                self.slot_repo.mark_available(new_slot_id)
                return None

            self.slot_repo.mark_available(appointment.appointment_slot_id)
            return updated_appointment
        except Exception:
            self.slot_repo.mark_available(new_slot_id)
            raise


class MarkNoShowUseCase:
    """Caso de uso para registrar no-show."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
    ):
        self.appointment_repo = appointment_repo

    def execute(self, appointment_id: int) -> Optional[Appointment]:
        appointment = self.appointment_repo.find_by_id(appointment_id)
        if not appointment:
            return None

        if appointment.status != AppointmentStatus.CONFIRMED:
            raise ValueError("Solo se pueden marcar como no-show citas confirmadas")

        return self.appointment_repo.mark_no_show(appointment_id)


class CompleteAppointmentUseCase:
    """Caso de uso para completar una cita."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
    ):
        self.appointment_repo = appointment_repo

    def execute(self, appointment_id: int) -> Optional[Appointment]:
        appointment = self.appointment_repo.find_by_id(appointment_id)
        if not appointment:
            return None

        if appointment.status not in [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.NO_SHOW,
        ]:
            raise ValueError("Solo se pueden completar citas confirmadas o en no-show")

        return self.appointment_repo.complete(appointment_id)


class GetAvailableSlotsUseCase:
    """Caso de uso para obtener franjas horarias disponibles."""

    def __init__(
        self,
        slot_repo: AppointmentSlotRepository,
    ):
        self.slot_repo = slot_repo

    def execute(self, clinic_id: int, branch_id: int) -> List[AppointmentSlot]:
        return self.slot_repo.find_available_slots_by_clinic_branch(
            clinic_id, branch_id
        )


class GetUserAppointmentsUseCase:
    """Caso de uso para obtener citas de un usuario."""

    def __init__(
        self,
        appointment_repo: AppointmentRepository,
    ):
        self.appointment_repo = appointment_repo

    def execute(self, owner_id: int) -> List[Appointment]:
        return self.appointment_repo.find_by_owner_id(owner_id)
