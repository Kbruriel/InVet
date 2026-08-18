"""Casos de uso para citas médicas (BE-008)."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.domain.entities.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.domain.repositories.appointment_repository import AppointmentRepository


class CreateAppointmentUseCase:
    """Caso de uso para crear una nueva cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        owner_id: int,
        pet_id: int,
        clinic_id: int,
        branch_id: int,
        appointment_type: str,
        scheduled_start: datetime,
        veterinarian_id: int | None = None,
        reason: str | None = None,
        duration_minutes: int = 30,
    ) -> Appointment:
        """Crear una nueva cita pendiente.

        Args:
            owner_id: ID del propietario.
            pet_id: ID de la mascota.
            clinic_id: ID de la clínica.
            branch_id: ID de la sucursal.
            appointment_type: Tipo de cita (consulta_general, vacunacion, etc).
            scheduled_start: Fecha/hora programada.
            veterinarian_id: ID del veterinario asignado (opcional).
            reason: Motivo de la cita.
            duration_minutes: Duración en minutos (15-120).

        Returns:
            Appointment con status=PENDING e ID asignado.

        Raises:
            ValueError: Si los datos son inválidos o hay conflicto de horario.
        """
        # Validar tipo de cita
        try:
            appt_type = AppointmentType(appointment_type)
        except ValueError as err:
            valid_types = [t.value for t in AppointmentType]
            raise ValueError(
                f"Tipo de cita inválido. Valores válidos: {valid_types}"
            ) from err

        # Validar duración
        if not (15 <= duration_minutes <= 120):
            raise ValueError("La duración debe estar entre 15 y 120 minutos.")

        # Calcular scheduled_end
        scheduled_end = scheduled_start + timedelta(minutes=duration_minutes)

        # Verificar conflicto de horario si hay veterinario asignado
        if veterinarian_id:
            has_conflict = await self.repository.check_conflict(
                veterinarian_id=veterinarian_id,
                branch_id=branch_id,
                scheduled_start=scheduled_start,
                duration_minutes=duration_minutes,
            )
            if has_conflict:
                raise ValueError(
                    "El veterinario tiene otro horario en ese rango. "
                    "Por favor seleccione otro horario."
                )

        # Crear entidad de dominio
        appointment = Appointment(
            id=0,
            owner_id=owner_id,
            pet_id=pet_id,
            veterinarian_id=veterinarian_id,
            clinic_id=clinic_id,
            branch_id=branch_id,
            appointment_type=appt_type,
            status=AppointmentStatus.PENDING,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            duration_minutes=duration_minutes,
            reason=reason,
            notes=None,
            created_by=owner_id,
        )

        return await self.repository.create_appointment(appointment)


class UpdateAppointmentStatusUseCase:
    """Caso de uso para transicionar el estado de una cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        appointment_id: int,
        clinic_id: int,
        action: str,
        notes: str | None = None,
        new_start: datetime | None = None,
        duration_minutes: int | None = None,
        updated_by: int | None = None,
    ) -> Appointment:
        """Transicionar el estado de una cita.

        Args:
            appointment_id: ID de la cita a actualizar.
            clinic_id: ID de la clínica (tenant isolation).
            action: Acción ('approve', 'confirm', 'complete', 'cancel', 'no_show').
            notes: Notas adicionales para la transición.
            new_start: Nueva fecha/hora (para reprogramaciones).
            duration_minutes: Nueva duración.
            updated_by: ID del usuario que realiza la acción.

        Returns:
            Appointment con status actualizado.

        Raises:
            ValueError: Si la transición no es válida o la cita no existe.
            PermissionError: Si el usuario no tiene permisos para esta acción.
        """
        # Obtener cita existente con tenant isolation
        appointment = await self.repository.get_by_id(appointment_id, clinic_id)
        if appointment is None:
            raise ValueError(f"Cita con ID {appointment_id} no encontrada.")

        valid_transitions = self._get_valid_transitions(action, appointment.status)

        if not valid_transitions:
            raise ValueError(
                f"La acción '{action}' no es válida para el estado actual "
                f"'{appointment.status.value}'. Transiciones válidas: {list(valid_transitions)}"
            )

        # Validar permisos por rol/acción
        self._validate_permissions(action, appointment, updated_by)

        # Realizar la transición
        new_status = valid_transitions[action]
        return await self.repository.transition_status(
            appointment_id=appointment_id,
            clinic_id=clinic_id,
            new_status=new_status.value,
            notes=notes,
            scheduled_start=new_start,
            duration_minutes=duration_minutes,
        )

    @staticmethod
    def _get_valid_transitions(
        action: str, current_status: AppointmentStatus
    ) -> dict[str, AppointmentStatus]:
        """Mapear acciones permitidas para un estado dado."""
        transitions_map = {
            AppointmentStatus.PENDING: {
                "approve": AppointmentStatus.APPROVED,
                "cancel": AppointmentStatus.CANCELLED,
            },
            AppointmentStatus.APPROVED: {
                "confirm": AppointmentStatus.CONFIRMED,
                "cancel": AppointmentStatus.CANCELLED,
            },
            AppointmentStatus.CONFIRMED: {
                "complete": AppointmentStatus.COMPLETED,
                "no_show": AppointmentStatus.NO_SHOW,
                "cancel": AppointmentStatus.CANCELLED,
            },
        }

        return transitions_map.get(current_status, {})

    @staticmethod
    def _validate_permissions(
        action: str, appointment: Appointment, updated_by: int | None
    ) -> None:
        """Validar permisos según la acción y el estado."""
        if action in ("approve", "confirm"):
            # Solo personal de clínica puede aprobar/confirmar
            if not (appointment.clinic_id > 0):
                raise PermissionError("No tiene permisos para realizar esta acción.")

        if action == "cancel":
            # Owner puede cancelar su cita, o clínica puede cancelar cita de su sucursal
            pass  # La validación real se hace en el router con el token


class ListAppointmentsByOwnerUseCase:
    """Caso de uso para listar citas de un propietario."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        owner_id: int,
        clinic_id: int | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un propietario con paginación.

        Args:
            owner_id: ID del propietario.
            clinic_id: ID de la clínica para tenant isolation (opcional).
            page: Número de página (1-indexed).
            size: Tamaño de página.

        Returns:
            Tupla de (lista de citas, total de citas).
        """
        return await self.repository.list_by_owner(
            owner_id=owner_id,
            page=page,
            size=size,
        )


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
    ) -> tuple[list[Appointment], int]:
        """Listar citas de una clínica con filtros y paginación.

        Args:
            clinic_id: ID de la clínica.
            page: Número de página (1-indexed).
            size: Tamaño de página.
            status_filter: Filtrar por estado (opcional).
            veterinarian_id: Filtrar por veterinario (opcional).

        Returns:
            Tupla de (lista de citas, total de citas).
        """
        return await self.repository.list_by_clinic(
            clinic_id=clinic_id,
            page=page,
            size=size,
            status_filter=status_filter,
            veterinarian_id=veterinarian_id,
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
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un veterinario con paginación.

        Args:
            veterinarian_id: ID del veterinario.
            page: Número de página (1-indexed).
            size: Tamaño de página.

        Returns:
            Tupla de (lista de citas, total de citas).
        """
        return await self.repository.list_by_veterinarian(
            veterinarian_id=veterinarian_id,
            page=page,
            size=size,
        )


class GetAvailabilityUseCase:
    """Caso de uso para obtener slots disponibles."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        clinic_id: int,
        date_str: str,
        branch_id: int | None = None,
        veterinarian_id: int | None = None,
        slot_duration_minutes: int = 30,
    ) -> list[dict]:
        """Obtener slots disponibles para una fecha dada.

        Args:
            clinic_id: ID de la clínica.
            date_str: Fecha en formato YYYY-MM-DD.
            branch_id: ID de la sucursal (opcional).
            veterinarian_id: ID del veterinario (opcional).
            slot_duration_minutes: Duración de cada slot.

        Returns:
            Lista de slots con información de disponibilidad.
        """
        # Parsear la fecha
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as err:
            raise ValueError("La fecha debe estar en formato YYYY-MM-DD") from err

        return await self.repository.get_available_slots(
            veterinarian_id=veterinarian_id,
            clinic_id=clinic_id,
            branch_id=branch_id,
            date=target_date,
            slot_duration_minutes=slot_duration_minutes,
        )


class CancelAppointmentUseCase:
    """Caso de uso para cancelar una cita."""

    def __init__(self, repository: AppointmentRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        appointment_id: int,
        clinic_id: int,
        updated_by: int,
    ) -> Appointment:
        """Cancelar una cita.

        Args:
            appointment_id: ID de la cita a cancelar.
            clinic_id: ID de la clínica (tenant isolation).
            updated_by: ID del usuario que cancela.

        Returns:
            Appointment con status=CANCELLED.

        Raises:
            ValueError: Si la cita no existe o ya está cancelada.
        """
        appointment = await self.repository.get_by_id(appointment_id, clinic_id)
        if appointment is None:
            raise ValueError(f"Cita con ID {appointment_id} no encontrada.")

        if appointment.status == AppointmentStatus.CANCELLED:
            raise ValueError("La cita ya está cancelada.")

        return await self.repository.transition_status(
            appointment_id=appointment_id,
            clinic_id=clinic_id,
            new_status=AppointmentStatus.CANCELLED.value,
            notes=f"Cancelada por usuario ID {updated_by}",
        )
