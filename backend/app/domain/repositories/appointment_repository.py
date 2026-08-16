"""Interfaces de repositorio para citas médicas (BE-008)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.appointment import Appointment


class AppointmentRepository(ABC):
    """Interface para el repositorio de citas."""

    @abstractmethod
    async def get_by_id(self, appointment_id: int, clinic_id: int) -> Appointment | None:
        """Obtener una cita por ID y clinic_id con tenant isolation."""
        pass

    @abstractmethod
    async def create_appointment(self, appointment: Appointment) -> Appointment:
        """Crear una nueva cita. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    async def update_appointment(
        self, appointment_id: int, clinic_id: int, data: dict
    ) -> Appointment | None:
        """Actualizar campos de una cita existente."""
        pass

    @abstractmethod
    async def transition_status(
        self,
        appointment_id: int,
        clinic_id: int,
        new_status: str,
        notes: str | None = None,
        scheduled_start: datetime | None = None,
        duration_minutes: int | None = None,
    ) -> Appointment | None:
        """Transicionar el estado de una cita."""
        pass

    @abstractmethod
    async def list_by_owner(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un propietario con paginación."""
        pass

    @abstractmethod
    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        status_filter: str | None = None,
        veterinarian_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de una clínica con filtros y paginación."""
        pass

    @abstractmethod
    async def list_by_veterinarian(
        self,
        veterinarian_id: int,
        page: int = 1,
        size: int = 20,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un veterinario con filtros."""
        pass

    @abstractmethod
    async def check_conflict(
        self,
        veterinarian_id: int,
        branch_id: int,
        scheduled_start: datetime,
        duration_minutes: int = 30,
        exclude_appointment_id: int | None = None,
    ) -> bool:
        """Verificar si existe un conflicto de horario para un veterinario."""
        pass

    @abstractmethod
    async def get_available_slots(
        self,
        veterinarian_id: int | None,
        clinic_id: int,
        branch_id: int | None,
        date: datetime,
        slot_duration_minutes: int = 30,
    ) -> list[dict]:
        """Obtener slots disponibles para un veterinario/clínica en una fecha."""
        pass
