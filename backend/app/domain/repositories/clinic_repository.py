"""Interfaces de repositorios para clínicas."""

from abc import ABC, abstractmethod

from app.domain.entities.clinic import Clinic


class ClinicRepository(ABC):
    """Interface para el repositorio de clínicas."""

    @abstractmethod
    async def search_clinics(
        self,
        location: str | None = None,
        service_type: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Clinic]:
        """Buscar clínicas según criterios especificados."""
        pass

    @abstractmethod
    async def get_clinic_count(
        self, location: str | None = None, service_type: str | None = None
    ) -> int:
        """Obtener el número total de clínicas que coinciden con los criterios."""
        pass
