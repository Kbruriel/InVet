"""Casos de uso para servicios (slice 006)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.service import Service
from app.domain.repositories.slice006_repositories import ServiceRepository


class CreateServiceUseCase:
    """Caso de uso para crear un servicio."""

    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    async def execute(self, data: dict[str, Any], clinic_id: int) -> Service:
        """Crear un nuevo servicio.

        Args:
            data: Diccionario con campos del servicio.
            clinic_id: ID de la clínica propietaria.

        Returns:
            Service con ID asignado.

        Raises:
            ValueError: Si faltan campos obligatorios o datos son inválidos.
        """
        # Validar campos obligatorios
        required_fields = ["name", "price", "duration_minutes"]
        for field in required_fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"El campo '{field}' es obligatorio.")

        price = float(data["price"])
        if price <= 0:
            raise ValueError("El precio debe ser mayor a cero.")

        duration = int(data["duration_minutes"])
        if duration <= 0:
            raise ValueError("La duración en minutos debe ser mayor a cero.")

        now = datetime.now(UTC)
        service = Service(
            id=0,
            clinic_id=clinic_id,
            name=str(data["name"]).strip(),
            description=str(data.get("description", "") or "") or None,
            price=price,
            duration_minutes=duration,
            is_active=data.get("is_active", True),
            created_at=now,
            updated_at=now,
        )

        # Verificar unicidad de nombre por clínica
        exists = await self.repository.exists_with_name(clinic_id, service.name)
        if exists:
            raise ValueError(f"Ya existe un servicio con el nombre '{service.name}' en esta clínica.")

        return await self.repository.create_service(service)


class GetServiceUseCase:
    """Caso de uso para obtener un servicio."""

    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    async def execute(self, service_id: int, clinic_id: int) -> Service | None:
        """Obtener un servicio por ID con tenant isolation.

        Args:
            service_id: ID del servicio.
            clinic_id: ID de la clínica.

        Returns:
            Service o None si no existe.
        """
        return await self.repository.get_service_by_id(service_id, clinic_id)


class UpdateServiceUseCase:
    """Caso de uso para actualizar un servicio."""

    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    async def execute(
        self, service_id: int, clinic_id: int, data: dict[str, Any]
    ) -> Service | None:
        """Actualizar un servicio existente.

        Args:
            service_id: ID del servicio.
            clinic_id: ID de la clínica.
            data: Campos a actualizar.

        Returns:
            Service actualizado o None si no existe.
        """
        # Validar precio si se proporciona
        if "price" in data and data["price"] is not None:
            price = float(data["price"])
            if price <= 0:
                raise ValueError("El precio debe ser mayor a cero.")

        # Validar duración si se proporciona
        if "duration_minutes" in data and data["duration_minutes"] is not None:
            duration = int(data["duration_minutes"])
            if duration <= 0:
                raise ValueError("La duración en minutos debe ser mayor a cero.")

        return await self.repository.update_service(service_id, clinic_id, data)


class DeactivateServiceUseCase:
    """Caso de uso para desactivar un servicio."""

    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    async def execute(self, service_id: int, clinic_id: int) -> Service | None:
        """Desactivar un servicio por ID.

        Args:
            service_id: ID del servicio.
            clinic_id: ID de la clínica.

        Returns:
            Service desactivado o None si no existe.
        """
        return await self.repository.deactivate_service(service_id, clinic_id)


class ListServicesUseCase:
    """Caso de uso para listar servicios."""

    def __init__(self, repository: ServiceRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[Service], int]:
        """Listar servicios de una clínica con paginación.

        Args:
            clinic_id: ID de la clínica.
            page: Número de página.
            size: Tamaño de página.
            is_active_only: Si True, solo retorna activos.

        Returns:
            Tuple de (lista de servicios, total).
        """
        return await self.repository.list_by_clinic(clinic_id, page, size, is_active_only)
