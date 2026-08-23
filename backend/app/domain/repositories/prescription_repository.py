"""Interfaces de repositorio para prescripciones (BE-010)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.prescription import Prescription


class PrescriptionRepository(ABC):
    """Interface para el repositorio de recetas veterinarias."""

    @abstractmethod
    async def create_prescription(self, prescription: Prescription) -> Prescription:
        """Crear receta atomica con items, tratamientos y recordatorios."""
        pass

    @abstractmethod
    async def get_by_id(
        self, prescription_id: int, clinic_id: int
    ) -> Prescription | None:
        """Obtener receta por ID con tenant isolation."""
        pass

    @abstractmethod
    async def exists_by_consultation(
        self, consultation_id: int, clinic_id: int
    ) -> bool:
        """Indica si ya existe receta para esa consulta (detectar duplicados)."""
        pass

    @abstractmethod
    async def list_by_pet(
        self,
        pet_id: int,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Prescription], int]:
        """Listar recetas de una mascota con paginacion y tenant isolation."""
        pass
