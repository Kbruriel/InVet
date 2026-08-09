"""Casos de uso para usuarios internos (slice 006)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.internal_user import InternalUser
from app.domain.repositories.slice006_repositories import InternalUserRepository


class CreateInternalUserUseCase:
    """Caso de uso para crear un usuario interno."""

    def __init__(self, repository: InternalUserRepository, db: Optional[Session] = None) -> None:
        self.repository = repository
        self.db = db

    async def execute(self, data: dict[str, Any], clinic_id: int) -> InternalUser:
        """Crear un nuevo usuario interno.

        Args:
            data: Diccionario con campos del usuario interno.
            clinic_id: ID de la clínica propietaria.

        Returns:
            InternalUser con ID asignado.

        Raises:
            ValueError: Si faltan campos obligatorios o datos son inválidos.
        """
        required_fields = ["user_id", "nombre", "rol"]
        for field in required_fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"El campo '{field}' es obligatorio.")

        user_id_val = int(data["user_id"])
        if user_id_val < 1:
            raise ValueError("El user_id debe ser mayor a cero.")

        # MJR-006-001: Validate that the referenced auth user exists (via repository interface)
        if hasattr(self.repository, 'check_user_exists') and self.db is not None:
            user_exists = await self.repository.check_user_exists(user_id_val, self.db)
            if not user_exists:
                raise ValueError(f"El usuario con ID {user_id_val} no existe en el sistema de autenticación.")

        # MJR-006-003: Validate branch_ids belong to the same clinic (via repository interface)
        branch_ids = data.get("branch_ids", []) or []
        if branch_ids and self.db is not None:
            if hasattr(self.repository, 'check_branches_belong_to_clinic'):
                invalid_branches = await self.repository.check_branches_belong_to_clinic(
                    [int(bid) for bid in branch_ids], clinic_id, self.db
                )
                if invalid_branches:
                    raise ValueError("Una o más sucursales no pertenecen a esta clínica.")

        now = datetime.now(UTC)
        internal_user = InternalUser(
            id=0,
            user_id=user_id_val,
            clinic_id=clinic_id,
            nombre=str(data["nombre"]).strip(),
            rol=str(data["rol"]).strip(),
            branch_ids=[int(bid) for bid in branch_ids] if branch_ids else [],
            is_active=data.get("is_active", True),
            created_at=now,
            updated_at=now,
        )

        return await self.repository.create_internal_user(internal_user)


class GetInternalUserUseCase:
    """Caso de uso para obtener un usuario interno."""

    def __init__(self, repository: InternalUserRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int, clinic_id: int) -> InternalUser | None:
        """Obtener un usuario interno por ID con tenant isolation.

        Args:
            user_id: ID del usuario interno.
            clinic_id: ID de la clínica.

        Returns:
            InternalUser o None si no existe.
        """
        return await self.repository.get_internal_user_by_id(user_id, clinic_id)


class UpdateInternalUserUseCase:
    """Caso de uso para actualizar un usuario interno."""

    def __init__(self, repository: InternalUserRepository) -> None:
        self.repository = repository

    async def execute(
        self, user_id: int, clinic_id: int, data: dict[str, Any]
    ) -> InternalUser | None:
        """Actualizar un usuario interno existente.

        Args:
            user_id: ID del usuario interno.
            clinic_id: ID de la clínica.
            data: Campos a actualizar.

        Returns:
            InternalUser actualizado o None si no existe.
        """
        return await self.repository.update_internal_user(user_id, clinic_id, data)


class DeactivateInternalUserUseCase:
    """Caso de uso para desactivar un usuario interno."""

    def __init__(self, repository: InternalUserRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: int, clinic_id: int) -> InternalUser | None:
        """Desactivar un usuario interno por ID.

        Args:
            user_id: ID del usuario interno.
            clinic_id: ID de la clínica.

        Returns:
            InternalUser desactivado o None si no existe.
        """
        return await self.repository.deactivate_internal_user(user_id, clinic_id)


class ListInternalUsersUseCase:
    """Caso de uso para listar usuarios internos."""

    def __init__(self, repository: InternalUserRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        is_active_only: bool = True,
    ) -> tuple[list[InternalUser], int]:
        """Listar usuarios internos de una clínica con paginación.

        Args:
            clinic_id: ID de la clínica.
            page: Número de página.
            size: Tamaño de página.
            is_active_only: Si True, solo retorna activos.

        Returns:
            Tuple de (lista de usuarios internos, total).
        """
        return await self.repository.list_by_clinic(clinic_id, page, size, is_active_only)


class AssignBranchToInternalUserUseCase:
    """Caso de uso para asignar sucursal a usuario interno."""

    def __init__(self, repository: InternalUserRepository) -> None:
        self.repository = repository

    async def execute(
        self, user_id: int, clinic_id: int, branch_id: int
    ) -> InternalUser | None:
        """Asignar una sucursal a un usuario interno.

        Args:
            user_id: ID del usuario interno.
            clinic_id: ID de la clínica.
            branch_id: ID de la sucursal.

        Returns:
            InternalUser actualizado o None si no existe.

        Raises:
            ValueError: Si el usuario no pertenece a esta clínica.
        """
        return await self.repository.assign_branch(user_id, clinic_id, branch_id)


class UnassignBranchFromInternalUserUseCase:
    """Caso de uso para desasignar sucursal de usuario interno."""

    def __init__(self, repository: InternalUserRepository) -> None:
        self.repository = repository

    async def execute(
        self, user_id: int, clinic_id: int, branch_id: int
    ) -> InternalUser | None:
        """Desasignar una sucursal de un usuario interno.

        Args:
            user_id: ID del usuario interno.
            clinic_id: ID de la clínica.
            branch_id: ID de la sucursal.

        Returns:
            InternalUser actualizado o None si no existe.
        """
        return await self.repository.unassign_branch(user_id, clinic_id, branch_id)
