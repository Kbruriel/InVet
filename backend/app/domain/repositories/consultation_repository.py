"""Interfaces de repositorio para consultas medicas (BE-009)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.consultation import Consultation


class ConsultationRepository(ABC):
    """Interface para el repositorio de consultas medicas."""

    @abstractmethod
    async def create_consultation(
        self, consultation: Consultation
    ) -> Consultation:
        """Crear una nueva consulta. Retorna la entidad con ID asignado."""
        pass

    @abstractmethod
    async def get_by_id(
        self, consultation_id: int, clinic_id: int
    ) -> Consultation | None:
        """Obtener una consulta por ID y clinic_id con tenant isolation."""
        pass

    @abstractmethod
    async def get_by_appointment_id(
        self, appointment_id: int, clinic_id: int
    ) -> Consultation | None:
        """Obtener la consulta asociada a una cita (para detectar duplicados)."""
        pass

    @abstractmethod
    async def list_by_pet(
        self,
        pet_id: int,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Consultation], int]:
        """Listar consultas de una mascota con paginacion y tenant isolation."""
        pass

    @abstractmethod
    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        pet_id: int | None = None,
    ) -> tuple[list[Consultation], int]:
        """Listar consultas de una clinica con filtros y paginacion."""
        pass
