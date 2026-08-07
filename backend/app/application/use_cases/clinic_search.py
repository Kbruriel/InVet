"""Casos de uso para búsqueda de clínicas."""

from __future__ import annotations

from app.api.v1.schemas.clinic_search import ClinicSearchResponse, ClinicSearchResult
from app.domain.repositories.clinic_repository import ClinicRepository


class SearchClinicsUseCase:
    """Caso de uso para buscar clínicas públicamente."""

    def __init__(self, clinic_repo: ClinicRepository):
        self.clinic_repo = clinic_repo

    async def execute(
        self,
        location: str | None = None,
        service_type: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> ClinicSearchResponse:
        """Buscar clínicas públicamente según criterios especificados.

        Solo se devuelven clínicas activas y visibles públicamente.

        Args:
            location: Ciudad o dirección para filtrar búsqueda
            service_type: Tipo de servicio para filtrar búsqueda
            page: Número de página (comienza en 1)
            size: Tamaño de página (máximo 100)

        Returns:
            Respuesta con resultados paginados

        Raises:
            ValueError: Si el tamaño de página no es válido.
        """
        if size < 1 or size > 100:
            raise ValueError("El tamaño de página debe estar entre 1 y 100")

        # Ejecutar búsqueda
        clinics = await self.clinic_repo.search_clinics(
            location=location,
            service_type=service_type,
            page=page,
            size=size,
        )

        # Convertir a tipo del schema (la entidad tiene campos más completos que el resultado de búsqueda)
        search_results = [
            ClinicSearchResult.model_validate(clinic) for clinic in clinics
        ]

        # Obtener conteo total
        total_clinics = await self.clinic_repo.get_clinic_count(
            location=location, service_type=service_type
        )

        # Calcular número de páginas
        total_pages = (total_clinics + size - 1) // size

        return ClinicSearchResponse(
            data=search_results,
            pagination={
                "page": page,
                "size": size,
                "total": total_clinics,
                "total_pages": total_pages,
            },
        )
