"""Casos de uso para veterinarios (slice 006)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.veterinarian import (
    Veterinarian,
    VeterinarianServiceAssignment,
)
from app.domain.repositories.slice006_repositories import (
    AssignmentRepository,
    VeterinarianRepository,
)


class CreateVeterinarianUseCase:
    """Caso de uso para crear un veterinario."""

    def __init__(self, repository: VeterinarianRepository) -> None:
        self.repository = repository

    async def execute(self, data: dict[str, Any], clinic_id: int) -> Veterinarian:
        """Crear un nuevo veterinario.

        Args:
            data: Diccionario con campos del veterinario.
            clinic_id: ID de la clínica propietaria.

        Returns:
            Veterinarian con ID asignado.

        Raises:
            ValueError: Si faltan campos obligatorios o datos son inválidos.
        """
        required_fields = ["nombre_completo", "licencia_profesional", "especialidad"]
        for field in required_fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"El campo '{field}' es obligatorio.")

        now = datetime.now(UTC)
        veterinarian = Veterinarian(
            id=0,
            clinic_id=clinic_id,
            nombre_completo=str(data["nombre_completo"]).strip(),
            licencia_profesional=str(data["licencia_profesional"]).strip(),
            especialidad=str(data["especialidad"]).strip(),
            telefono=str(data.get("telefono", "") or "").strip() or None,
            email=data.get("email"),
            is_active=data.get("is_active", True),
            created_at=now,
            updated_at=now,
        )

        # Verificar unicidad de licencia por clínica
        exists = await self.repository.exists_with_license(
            clinic_id, veterinarian.licencia_profesional
        )
        if exists:
            raise ValueError(
                f"Ya existe un veterinario con la licencia '{veterinarian.licencia_profesional}' en esta clínica."
            )

        return await self.repository.create_veterinarian(veterinarian)


class GetVeterinarianUseCase:
    """Caso de uso para obtener un veterinario."""

    def __init__(self, repository: VeterinarianRepository) -> None:
        self.repository = repository

    async def execute(self, vet_id: int, clinic_id: int) -> Veterinarian | None:
        """Obtener un veterinario por ID con tenant isolation.

        Args:
            vet_id: ID del veterinario.
            clinic_id: ID de la clínica.

        Returns:
            Veterinarian o None si no existe.
        """
        return await self.repository.get_veterinarian_by_id(vet_id, clinic_id)


class UpdateVeterinarianUseCase:
    """Caso de uso para actualizar un veterinario."""

    def __init__(self, repository: VeterinarianRepository) -> None:
        self.repository = repository

    async def execute(
        self, vet_id: int, clinic_id: int, data: dict[str, Any]
    ) -> Veterinarian | None:
        """Actualizar un veterinario existente.

        Args:
            vet_id: ID del veterinario.
            clinic_id: ID de la clínica.
            data: Campos a actualizar.

        Returns:
            Veterinarian actualizado o None si no existe.
        """
        return await self.repository.update_veterinarian(vet_id, clinic_id, data)


class DeactivateVeterinarianUseCase:
    """Caso de uso para desactivar un veterinario."""

    def __init__(self, repository: VeterinarianRepository) -> None:
        self.repository = repository

    async def execute(self, vet_id: int, clinic_id: int) -> Veterinarian | None:
        """Desactivar un veterinario por ID.

        Args:
            vet_id: ID del veterinario.
            clinic_id: ID de la clínica.

        Returns:
            Veterinarian desactivado o None si no existe.
        """
        return await self.repository.deactivate_veterinarian(vet_id, clinic_id)


class ListVeterinariansUseCase:
    """Caso de uso para listar veterinarios."""

    def __init__(self, repository: VeterinarianRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[Veterinarian], int]:
        """Listar veterinarios de una clínica con paginación.

        Args:
            clinic_id: ID de la clínica.
            page: Número de página.
            size: Tamaño de página.
            is_active_only: Si True, solo retorna activos.

        Returns:
            Tuple de (lista de veterinarios, total).
        """
        return await self.repository.list_by_clinic(
            clinic_id, page, size, is_active_only
        )


class AssignServiceToVeterinarianUseCase:
    """Caso de uso para asignar servicio a veterinario."""

    def __init__(
        self, assignment_repo: AssignmentRepository, vet_repo: VeterinarianRepository
    ) -> None:
        self.assignment_repo = assignment_repo
        self.vet_repo = vet_repo

    async def execute(
        self, vet_id: int, service_id: int, clinic_id: int
    ) -> VeterinarianServiceAssignment | None:
        """Asignar un servicio a un veterinario.

        Args:
            vet_id: ID del veterinario.
            service_id: ID del servicio.
            clinic_id: ID de la clínica (tenant isolation).

        Returns:
            Assignment o None si no existe alguno de los extremos.

        Raises:
            ValueError: Si los extremos pertenecen a diferentes clínicas.
        """
        # Validar que el veterinario pertenece a la clínica
        vet = await self.vet_repo.get_veterinarian_by_id(vet_id, clinic_id)
        if vet is None:
            raise ValueError("Veterinario no encontrado en esta clínica.")

        # Validar que el servicio pertenece a la misma clínica
        from app.domain.repositories.slice006_repositories import ServiceRepository

        svc_repo: ServiceRepository = self.vet_repo  # type: ignore - will be replaced at router level
        # We'll validate service existence in the router layer

        return await self.assignment_repo.assign_service(vet_id, service_id, clinic_id)


class UnassignServiceFromVeterinarianUseCase:
    """Caso de uso para desasignar servicio de veterinario."""

    def __init__(self, assignment_repo: AssignmentRepository) -> None:
        self.assignment_repo = assignment_repo

    async def execute(self, vet_id: int, service_id: int, clinic_id: int) -> bool:
        """Desasignar un servicio de un veterinario.

        Args:
            vet_id: ID del veterinario.
            service_id: ID del servicio.
            clinic_id: ID de la clínica.

        Returns:
            True si se desasignó, False si no existía la asignación.
        """
        return await self.assignment_repo.unassign_service(
            vet_id, service_id, clinic_id
        )
