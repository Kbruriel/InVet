"""Casos de uso para consultas médicas (BE-009)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.domain.entities.appointment import AppointmentStatus
from app.domain.entities.consultation import (
    Consultation,
    ConsultationCreate,
)
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.consultation_repository import ConsultationRepository

# Resuelve el owner_id de una mascota (inyectado por el router para no
# acoplar el caso de uso a un repositorio de mascotas concreto).
PetOwnerResolver = Callable[[int, int], Awaitable[int | None]]


class ConsultationError(Exception):
    """Error base de casos de uso de consultas."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AppointmentNotCompletedError(ConsultationError):
    """La cita no está en estado completed (map a 422)."""


class DuplicateConsultationError(ConsultationError):
    """Ya existe una consulta para esa cita (map a 409)."""


class OwnershipError(ConsultationError):
    """El usuario no tiene acceso a la mascota/consulta (map a 403)."""


class ConsultationNotFoundError(ConsultationError):
    """La consulta no existe o no es visible por el tenant (map a 404)."""


class CreateConsultationUseCase:
    """Crear una consulta médica para una cita completada.

    Reglas de negocio:
    - La cita debe existir en la misma clínica.
    - La cita debe estar en estado ``completed`` (error 422).
    - No puede existir otra consulta para la misma cita (error 409).
    - La mascota debe pertenecer al owner indicado (error 403).
    """

    def __init__(
        self,
        consultation_repository: ConsultationRepository,
        appointment_repository: AppointmentRepository,
        pet_owner_resolver: PetOwnerResolver | None = None,
    ) -> None:
        self.consultation_repository = consultation_repository
        self.appointment_repository = appointment_repository
        self.pet_owner_resolver = pet_owner_resolver

    async def execute(
        self,
        data: ConsultationCreate,
        owner_id: int | None = None,
        created_by: int | None = None,
    ) -> Consultation:
        """Crear la consulta validando estado de la cita y duplicados.

        Args:
            data: Datos de la consulta (clinic_id ya resuelto en el router).
            owner_id: Owner legítimo de la mascota (resuelto en el router).
            created_by: ID del usuario interno que creó la consulta.

        Returns:
            Consultation con ID asignado.

        Raises:
            AppointmentNotCompletedError: La cita no está completed.
            DuplicateConsultationError: Ya existe consulta para esa cita.
            OwnershipError: La mascota no pertenece al owner.
        """
        appointment = await self.appointment_repository.get_by_id(
            data.appointment_id, data.clinic_id
        )
        if appointment is None:
            raise OwnershipError("La cita no existe o no es accesible.")

        if appointment.status != AppointmentStatus.COMPLETED:
            raise AppointmentNotCompletedError(
                "Solo se puede registrar una consulta cuando la cita está "
                "completada (estado 'completed')."
            )

        if appointment.pet_id != data.pet_id:
            raise OwnershipError("La mascota no coincide con la cita.")

        appointment_owner_id = appointment.owner_id if owner_id is None else owner_id
        if self.pet_owner_resolver is not None:
            pet_owner_id = await self.pet_owner_resolver(data.pet_id, data.clinic_id)
            if pet_owner_id != appointment_owner_id:
                raise OwnershipError("La mascota no pertenece al usuario.")

        existing = await self.consultation_repository.get_by_appointment_id(
            data.appointment_id, data.clinic_id
        )
        if existing is not None:
            raise DuplicateConsultationError(
                "Ya existe una consulta registrada para esta cita."
            )

        resolved_branch_id = data.branch_id if data.branch_id is not None else appointment.branch_id
        resolved_veterinarian_id = (
            data.veterinarian_id
            if data.veterinarian_id is not None
            else appointment.veterinarian_id
        )

        consultation = Consultation(
            id=None,
            appointment_id=data.appointment_id,
            pet_id=data.pet_id,
            clinic_id=data.clinic_id,
            branch_id=resolved_branch_id,
            veterinarian_id=resolved_veterinarian_id,
            history=data.history or "",
            diagnosis=data.diagnosis,
            recommendations=data.recommendations or "",
            created_by=created_by,
        )
        return await self.consultation_repository.create_consultation(consultation)


class GetConsultationUseCase:
    """Obtener una consulta por ID con tenant isolation."""

    def __init__(self, repository: ConsultationRepository) -> None:
        self.repository = repository

    async def execute(self, consultation_id: int, clinic_id: int) -> Consultation:
        """Retornar la consulta o lanzar ConsultationNotFoundError."""
        consultation = await self.repository.get_by_id(consultation_id, clinic_id)
        if consultation is None:
            raise ConsultationNotFoundError("La consulta no existe.")
        return consultation


class ListConsultationsUseCase:
    """Listar consultas con paginación y tenant isolation."""

    def __init__(self, repository: ConsultationRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        pet_id: int | None = None,
    ) -> tuple[list[Consultation], int]:
        """Listar consultas de una clínica, opcionalmente filtradas por mascota."""
        return await self.repository.list_by_clinic(
            clinic_id=clinic_id, page=page, size=size, pet_id=pet_id
        )
