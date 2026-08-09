"""Casos de uso para CRUD de clinica."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.domain.entities.clinic import Clinic
from app.domain.repositories.clinic_repository import ClinicRepository


class CreateClinicUseCase:
    """Caso de uso para crear una clínica."""

    def __init__(self, repository: ClinicRepository) -> None:
        self.repository = repository

    async def execute(self, data: dict[str, Any]) -> Clinic:
        """Crear una nueva clínica.

        Args:
            data: Diccionario con campos de la clínica (name, address, city, state, country, postal_code, phone, email).

        Returns:
            Clinic con ID asignado.

        Raises:
            ValueError: Si faltan campos obligatorios o datos son invalidos.
        """
        # Validar campos obligatorios
        required_fields = ["name", "address", "city", "state", "country", "postal_code"]
        for field in required_fields:
            value = data.get(field)
            if not value or not str(value).strip():
                raise ValueError(f"El campo '{field}' es obligatorio.")

        now = datetime.now(UTC)
        clinic = Clinic(
            id=0,  # Se asigna en el repositorio
            name=str(data["name"]).strip(),
            description=str(data.get("description", "")) or None,
            address=str(data["address"]).strip(),
            city=str(data["city"]).strip(),
            state=str(data["state"]).strip(),
            country=str(data["country"]).strip(),
            postal_code=str(data["postal_code"]).strip(),
            phone=str(data.get("phone", "")).strip() or None,
            email=str(data.get("email", "")).strip() or None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return await self.repository.create_clinic(clinic)


class UpdateClinicUseCase:
    """Caso de uso para actualizar una clínica."""

    def __init__(self, repository: ClinicRepository) -> None:
        self.repository = repository

    async def execute(self, clinic_id: int, data: dict[str, Any]) -> Clinic | None:
        """Actualizar una clínica existente.

        Args:
            clinic_id: ID de la clínica a actualizar.
            data: Diccionario con campos a actualizar.

        Returns:
            Clinic actualizada o None si no existe.
        """
        allowed_fields = [
            "name",
            "description",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "phone",
            "email",
        ]
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not filtered_data:
            raise ValueError("No hay campos válidos para actualizar.")

        return await self.repository.update_clinic(clinic_id, filtered_data)


class GetClinicUseCase:
    """Caso de uso para obtener una clínica por ID."""

    def __init__(self, repository: ClinicRepository) -> None:
        self.repository = repository

    async def execute(self, clinic_id: int) -> Clinic | None:
        """Obtener una clínica por ID.

        Args:
            clinic_id: ID de la clínica.

        Returns:
            Clinic o None si no existe.
        """
        return await self.repository.get_clinic_by_id(clinic_id)


class DeactivateClinicUseCase:
    """Caso de uso para inactivar una clínica."""

    def __init__(self, repository: ClinicRepository) -> None:
        self.repository = repository

    async def execute(self, clinic_id: int) -> Clinic | None:
        """Inactivar una clínica por ID.

        Returns:
            Clinic inactivada o None si no existe.
        """
        return await self.repository.deactivate_clinic(clinic_id)


class ActivateClinicUseCase:
    """Caso de uso para reactivar una clínica."""

    def __init__(self, repository: ClinicRepository) -> None:
        self.repository = repository

    async def execute(self, clinic_id: int) -> Clinic | None:
        """Reactivar una clínica inactiva por ID.

        Returns:
            Clinic reactivada o None si no existe.
        """
        return await self.repository.activate_clinic(clinic_id)


class ListClinicsUseCase:
    """Caso de uso para listar clínicas de un tenant."""

    def __init__(self, repository: ClinicRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        tenant_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Clinic], int]:
        """Listar clínicas de un tenant con paginación.

        Args:
            tenant_id: ID del tenant/propietario.
            page: Número de página (1-based).
            size: Tamaño de página.

        Returns:
            Tuple de (lista de clinicas, total de resultados).
        """
        return await self.repository.list_clinics_by_tenant(tenant_id, page, size)
