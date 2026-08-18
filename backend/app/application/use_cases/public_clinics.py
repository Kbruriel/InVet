"""Casos de uso para clnicas pblicas."""

from __future__ import annotations

from app.api.v1.schemas.public_clinic import (
    PublicClinicDetailDTO,
    PublicClinicListDTO,
    PublicClinicsPaginatedResponse,
)
from app.domain.repositories.clinic_repository import ClinicRepository


class ListPublicClinicsUseCase:
    """Caso de uso para listar clnicas pblicamente."""

    def __init__(self, clinic_repo: ClinicRepository):
        self.clinic_repo = clinic_repo

    async def execute(
        self,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        service_type: str | None = None,
    ) -> PublicClinicsPaginatedResponse:
        """Listar clnicas pblicas segn criterios especificados.

        Args:
            page: Nmero de pgina (comienza en 1)
            size: Tamao de pgina (mximo 100)
            search: Filtro por nombre o ciudad
            service_type: Filtro por tipo de servicio

        Returns:
            Respuesta con resultados paginados

        Raises:
            ValueError: Si el tamao de pgina no es vlido.
        """
        if size < 1 or size > 100:
            raise ValueError("El tamao de pgina debe estar entre 1 y 100")

        # Ejecutar bsqueda
        clinics = await self.clinic_repo.search_clinics(
            location=search,
            service_type=service_type,
            page=page,
            size=size,
        )

        # Convertir a DTOs pblicos (sin campos internos)
        search_results = [
            PublicClinicListDTO.model_validate(clinic) for clinic in clinics
        ]

        # Obtener conteo total
        total_clinics = await self.clinic_repo.get_clinic_count(
            location=search, service_type=service_type
        )

        # Calcular nmero de pginas
        total_pages = (total_clinics + size - 1) // size

        return PublicClinicsPaginatedResponse(
            data=search_results,
            pagination={
                "page": page,
                "size": size,
                "total": total_clinics,
                "total_pages": total_pages,
            },
        )

    async def get_by_id(self, clinic_id: int) -> PublicClinicDetailDTO | None:
        """Obtener detalle de una clnica pblica por ID.

        Args:
            clinic_id: ID de la clnica

        Returns:
            DTO con detalle o None si no existe
        """
        clinic = await self.clinic_repo.get_clinic_by_id(clinic_id)
        if not clinic:
            return None

        return PublicClinicDetailDTO.model_validate(clinic)
