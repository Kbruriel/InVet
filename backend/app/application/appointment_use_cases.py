"""Casos de uso para citas médicas (BE-008)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domain.entities.appointment import (
    Appointment,
    AppointmentCreate,
    AppointmentStatus,
)
from app.domain.repositories.appointment_repository import AppointmentRepository

# Transiciones validas (según BE-008 plan, §Máquina de estados):
#   pending    -> approved, cancelled, rescheduled
#   approved   -> confirmed, cancelled, rescheduled
#   confirmed  -> completed, no_show, cancelled, rescheduled
#   rescheduled -> pending, cancelled
#   completed / no_show / cancelled -> TERMINAL (sin transiciones)
_VALID_TRANSITIONS: dict[str, set[str]] = {
    AppointmentStatus.PENDING.value: {
        AppointmentStatus.APPROVED.value,
        AppointmentStatus.CANCELLED.value,
        AppointmentStatus.RESCHEDULED.value,
    },
    AppointmentStatus.APPROVED.value: {
        AppointmentStatus.CONFIRMED.value,
        AppointmentStatus.CANCELLED.value,
        AppointmentStatus.RESCHEDULED.value,
    },
    AppointmentStatus.CONFIRMED.value: {
        AppointmentStatus.COMPLETED.value,
        AppointmentStatus.NO_SHOW.value,
        AppointmentStatus.CANCELLED.value,
        AppointmentStatus.RESCHEDULED.value,
    },
    AppointmentStatus.RESCHEDULED.value: {
        AppointmentStatus.PENDING.value,
        AppointmentStatus.CANCELLED.value,
    },
}


class CreateAppointmentUseCase:
    """Caso de uso para crear una cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self, data: AppointmentCreate, owner_id: int, created_by: int | None = None
    ) -> Appointment:
        """Crear una nueva cita pendiente.

        Args:
            data: Datos de la cita.
            owner_id: ID del propietario que solicita.
            created_by: ID del usuario interno que creó (si aplica).

        Returns:
            Appointment con ID asignado.

        Raises:
            ValueError: Si hay conflicto de horario o datos inválidos.
        """
        if data.veterinarian_id is not None:
            has_conflict = await self.repository.check_conflict(
                veterinarian_id=data.veterinarian_id,
                branch_id=data.branch_id,
                scheduled_start=data.scheduled_start,
                duration_minutes=data.duration_minutes,
            )
            if has_conflict:
                raise ValueError(
                    "El veterinario seleccionado ya tiene una cita en ese horario."
                )

        appointment = Appointment(
            id=0,
            owner_id=owner_id,
            pet_id=data.pet_id,
            veterinarian_id=data.veterinarian_id,
            clinic_id=data.clinic_id,
            branch_id=data.branch_id,
            appointment_type=data.appointment_type,
            status=AppointmentStatus.PENDING,
            scheduled_start=data.scheduled_start,
            scheduled_end=data.scheduled_end,
            duration_minutes=data.duration_minutes,
            reason=data.reason,
            notes=data.notes,
            created_by=created_by,
        )
        return await self.repository.create_appointment(appointment)


class UpdateAppointmentUseCase:
    """Caso de uso para actualizar una cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        appointment_id: int,
        clinic_id: int,
        data: dict[str, Any],
    ) -> Appointment | None:
        """Actualizar campos de una cita existente.

        Args:
            appointment_id: ID de la cita.
            clinic_id: ID de la clínica (tenant isolation).
            data: Campos a actualizar.

        Returns:
            Appointment actualizado o None si no existe.
        """
        return await self.repository.update_appointment(appointment_id, clinic_id, data)


class TransitionAppointmentStatusUseCase:
    """Caso de uso para transicionar el estado de una cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        appointment_id: int,
        clinic_id: int,
        new_status: str,
        notes: str | None = None,
        scheduled_start: datetime | None = None,
        duration_minutes: int | None = None,
    ) -> Appointment | None:
        """Transicionar el estado de una cita.

        Args:
            appointment_id: ID de la cita.
            clinic_id: ID de la clínica (tenant isolation).
            new_status: Nuevo estado deseado.
            notes: Notas de la transición.
            scheduled_start: Nueva fecha (solo para reprogramación).
            duration_minutes: Nueva duración (solo para reprogramación).

        Raises:
            ValueError: Si la transición no es válida.
        """
        appointment = await self.repository.get_by_id(appointment_id, clinic_id)
        if appointment is None:
            return None

        current_status = appointment.status.value
        allowed = _VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Transición inválida de '{current_status}' a '{new_status}'."
            )

        return await self.repository.transition_status(
            appointment_id=appointment_id,
            clinic_id=clinic_id,
            new_status=new_status,
            notes=notes,
            scheduled_start=scheduled_start,
            duration_minutes=duration_minutes,
        )


class GetAppointmentUseCase:
    """Caso de uso para obtener una cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(self, appointment_id: int, clinic_id: int) -> Appointment | None:
        """Obtener una cita por ID con tenant isolation.

        Args:
            appointment_id: ID de la cita.
            clinic_id: ID de la clínica.

        Returns:
            Appointment o None si no existe.
        """
        return await self.repository.get_by_id(appointment_id, clinic_id)


class ListAppointmentsByOwnerUseCase:
    """Caso de uso para listar citas de un propietario."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un propietario con paginación.

        Args:
            owner_id: ID del propietario.
            page: Número de página.
            size: Elementos por página.

        Returns:
            Tuple (lista de citas, total).
        """
        return await self.repository.list_by_owner(owner_id, page, size)


class ListAppointmentsByClinicUseCase:
    """Caso de uso para listar citas de una clínica."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        status_filter: str | None = None,
        veterinarian_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de una clínica con filtros.

        Args:
            clinic_id: ID de la clínica.
            page: Número de página.
            size: Elementos por página.
            status_filter: Filtrar por estado.
            veterinarian_id: Filtrar por veterinario.
            date_from: Fecha inicio rango.
            date_to: Fecha fin rango.

        Returns:
            Tuple (lista de citas, total).
        """
        return await self.repository.list_by_clinic(
            clinic_id=clinic_id,
            page=page,
            size=size,
            status_filter=status_filter,
            veterinarian_id=veterinarian_id,
            date_from=date_from,
            date_to=date_to,
        )


class ListAppointmentsByVeterinarianUseCase:
    """Caso de uso para listar citas de un veterinario."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        veterinarian_id: int,
        page: int = 1,
        size: int = 20,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un veterinario con filtros.

        Args:
            veterinarian_id: ID del veterinario.
            page: Número de página.
            size: Elementos por página.
            date_from: Fecha inicio rango.
            date_to: Fecha fin rango.

        Returns:
            Tuple (lista de citas, total).
        """
        return await self.repository.list_by_veterinarian(
            veterinarian_id=veterinarian_id,
            page=page,
            size=size,
            date_from=date_from,
            date_to=date_to,
        )


class GetAvailabilityUseCase:
    """Caso de uso para obtener disponibilidad de horarios."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        veterinarian_id: int | None,
        clinic_id: int,
        branch_id: int | None,
        date: datetime,
        slot_duration_minutes: int = 30,
    ) -> list[dict]:
        """Obtener slots disponibles.

        Args:
            veterinarian_id: ID del veterinario (None = todos).
            clinic_id: ID de la clínica.
            branch_id: ID de la sucursal (opcional).
            date: Fecha a consultar.
            slot_duration_minutes: Duración de cada slot.

        Returns:
            Lista de slots disponibles.
        """
        return await self.repository.get_available_slots(
            veterinarian_id=veterinarian_id,
            clinic_id=clinic_id,
            branch_id=branch_id,
            date=date,
            slot_duration_minutes=slot_duration_minutes,
        )
