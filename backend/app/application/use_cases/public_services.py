"""Casos de uso para servicios pblicos."""

from __future__ import annotations

from app.api.v1.schemas.public_service import (
    PublicServiceListDTO,
    PublicServicesPaginatedResponse,
)
from app.domain.repositories.branch_repository import ServiceRepository


class ListPublicServicesUseCase:
    """Caso de uso para listar servicios pblicamente."""

    def __init__(self, service_repo: ServiceRepository):
        self.service_repo = service_repo

    async def execute(
        self,
        page: int = 1,
        size: int = 20,
        sucursal_id: int | None = None,
        clinica_id: int | None = None,
        search: str | None = None,
    ) -> PublicServicesPaginatedResponse:
        """Listar servicios pblicos segn criterios especificados.

        Args:
            page: Nmero de pgina (comienza en 1)
            size: Tamao de pgina (mximo 100)
            sucursal_id: Filtro por ID de sucursal
            clinica_id: Filtro por ID de clnica
            search: Filtro por nombre del servicio

        Returns:
            Respuesta con resultados paginados

        Raises:
            ValueError: Si el tamao de pgina no es vlido.
        """
        if size < 1 or size > 100:
            raise ValueError("El tamao de pgina debe estar entre 1 y 100")

        # Obtener servicios con paginacin a nivel de base de datos
        services, total_services = await self.service_repo.list_public_services(
            sucursal_id=sucursal_id,
            clinica_id=clinica_id,
            search=search,
            page=page,
            size=size,
        )

        if not services:
            services = []

        # Convertir a DTOs pblicos (sin campos internos como created_at, updated_at)
        search_results = [
            PublicServiceListDTO.model_validate(service) for service in services
        ]

        # Calcular nmero de pginas
        total_pages = (total_services + size - 1) // size if total_services > 0 else 0

        return PublicServicesPaginatedResponse(
            data=search_results,
            pagination={
                "page": page,
                "size": size,
                "total": total_services,
                "total_pages": total_pages,
            },
        )
