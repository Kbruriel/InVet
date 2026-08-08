"""Casos de uso para sucursales pblicas."""

from __future__ import annotations

from app.api.v1.schemas.public_branch import (
    PublicBranchesPaginatedResponse,
    PublicBranchListDTO,
)
from app.domain.repositories.branch_repository import BranchRepository


class ListPublicBranchesUseCase:
    """Caso de uso para listar sucursales pblicamente."""

    def __init__(self, branch_repo: BranchRepository):
        self.branch_repo = branch_repo

    async def execute(
        self,
        page: int = 1,
        size: int = 20,
        clinica_id: int | None = None,
        search: str | None = None,
    ) -> PublicBranchesPaginatedResponse:
        """Listar sucursales pblicas segn criterios especificados.

        Args:
            page: Nmero de pgina (comienza en 1)
            size: Tamao de pgina (mximo 100)
            clinica_id: Filtro por ID de clnica
            search: Filtro por nombre o ciudad

        Returns:
            Respuesta con resultados paginados

        Raises:
            ValueError: Si el tamao de pgina no es vlido.
        """
        if size < 1 or size > 100:
            raise ValueError("El tamao de pgina debe estar entre 1 y 100")

        # Obtener sucursales con paginacin a nivel de base de datos
        branches, total_branches = await self.branch_repo.list_public_branches(
            clinica_id=clinica_id, search=search, page=page, size=size
        )

        if not branches:
            branches = []

        # Convertir a DTOs pblicos (sin campos internos como created_at, updated_at, postal_code, email)
        search_results = [
            PublicBranchListDTO.model_validate(branch) for branch in branches
        ]

        # Calcular nmero de pginas
        total_pages = (total_branches + size - 1) // size if total_branches > 0 else 0

        return PublicBranchesPaginatedResponse(
            data=search_results,
            pagination={
                "page": page,
                "size": size,
                "total": total_branches,
                "total_pages": total_pages,
            },
        )
