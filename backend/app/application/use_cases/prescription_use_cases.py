"""Casos de uso para recetas veterinarias (BE-010)."""

from __future__ import annotations

from app.domain.entities.appointment import AppointmentStatus
from app.domain.entities.prescription import Prescription, PrescriptionCreate
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.consultation_repository import ConsultationRepository
from app.domain.repositories.prescription_repository import PrescriptionRepository


class PrescriptionError(Exception):
    """Error base de casos de uso de prescripciones."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConsultationNotCompletedError(PrescriptionError):
    """La consulta/cita no está en estado completed (map a 422)."""


class ConsultationInvalidError(PrescriptionError):
    """La consulta no existe o no es accesible (map a 422 en creacion)."""


class DuplicatePrescriptionError(PrescriptionError):
    """Ya existe una receta para esa consulta (map a 409)."""


class PrescriptionNotFoundError(PrescriptionError):
    """La receta no existe o no es visible por el tenant (map a 404)."""


class OwnershipError(PrescriptionError):
    """El usuario no tiene acceso a la mascota/receta (map a 403)."""


class CreatePrescriptionUseCase:
    """Crear una receta veterinaria ligada a una consulta completed.

    Reglas de negocio:
    - La consulta debe existir en la misma clínica (404).
    - La cita asociada a la consulta debe estar ``completed`` (422).
    - La mascota debe coincidir con la consulta (403).
    - No puede existir otra receta para la misma consulta (409).
    """

    def __init__(
        self,
        prescription_repository: PrescriptionRepository,
        consultation_repository: ConsultationRepository,
        appointment_repository: AppointmentRepository,
    ) -> None:
        self.prescription_repository = prescription_repository
        self.consultation_repository = consultation_repository
        self.appointment_repository = appointment_repository

    async def execute(self, data: PrescriptionCreate) -> Prescription:
        """Crear la receta validando consulta completed, mascota y duplicados.

        Raises:
            ConsultationInvalidError: La consulta no existe o no es accesible.
            ConsultationNotCompletedError: La cita no está completed.
            OwnershipError: La mascota no coincide con la consulta.
            DuplicatePrescriptionError: Ya existe receta para esa consulta.
        """
        consultation = await self.consultation_repository.get_by_id(
            data.consultation_id, data.clinic_id
        )
        if consultation is None:
            raise ConsultationInvalidError("La consulta no existe o no es accesible.")

        appointment = await self.appointment_repository.get_by_id(
            consultation.appointment_id, data.clinic_id
        )
        if (
            appointment is not None
            and appointment.status != AppointmentStatus.COMPLETED
        ):
            raise ConsultationNotCompletedError(
                "Solo se puede registrar una receta cuando la cita está "
                "completada (estado 'completed')."
            )

        if consultation.pet_id != data.pet_id:
            raise OwnershipError("La mascota no coincide con la consulta.")

        if await self.prescription_repository.exists_by_consultation(
            data.consultation_id, data.clinic_id
        ):
            raise DuplicatePrescriptionError(
                "Ya existe una receta registrada para esta consulta."
            )

        prescription = Prescription(
            id=None,
            consultation_id=data.consultation_id,
            pet_id=data.pet_id,
            clinic_id=data.clinic_id,
            branch_id=consultation.branch_id,
            veterinarian_id=data.veterinarian_id or consultation.veterinarian_id,
            diagnosis=data.diagnosis,
            treatment_notes=data.treatment_notes or "",
            created_by=data.created_by,
            items=data.items,
            treatments=data.treatments,
            reminders=data.reminders,
        )
        return await self.prescription_repository.create_prescription(prescription)


class GetPrescriptionUseCase:
    """Obtener una receta por ID con tenant isolation."""

    def __init__(self, repository: PrescriptionRepository) -> None:
        self.repository = repository

    async def execute(self, prescription_id: int, clinic_id: int) -> Prescription:
        """Retornar la receta o lanzar PrescriptionNotFoundError."""
        prescription = await self.repository.get_by_id(prescription_id, clinic_id)
        if prescription is None:
            raise PrescriptionNotFoundError("La receta no existe.")
        return prescription


class ListPrescriptionsUseCase:
    """Listar recetas por mascota con paginación y tenant isolation."""

    def __init__(self, repository: PrescriptionRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        pet_id: int,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Prescription], int]:
        """Listar recetas de una mascota con paginación."""
        return await self.repository.list_by_pet(
            pet_id=pet_id, clinic_id=clinic_id, page=page, size=size
        )
