"""Use cases para soporter basico (BE-014).

Servicio de dominio que centraliza la logica de creacion/listado/detalle/actualizacion
de tickets de soporte con guardas de estado y transiciones validadas.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime, timedelta
from typing import Any

from app.data.support_ticket_repo import SupportTicketRepository

# ================================================================== #
# Enum canonico de estados (coincide con dominio)
# ================================================================== #


class TicketStatus(str, enum.Enum):
    INICIADO = "iniciado"
    PENDIENTE = "pendiente"
    PROCESO = "proceso"
    COMPLETADO = "completado"
    CERRADO = "cerrado"


# ================================================================== #
# Transiciones validas por estado actual (AC-014-05)
# ================================================================== #

_TRANSITIONS: dict[str, frozenset[str]] = {
    TicketStatus.INICIADO.value: frozenset(
        [TicketStatus.PENDIENTE.value, TicketStatus.PROCESO.value]
    ),
    TicketStatus.PENDIENTE.value: frozenset([TicketStatus.PROCESO.value]),
    TicketStatus.PROCESO.value: frozenset(
        [TicketStatus.COMPLETADO.value, TicketStatus.CERRADO.value]
    ),
    TicketStatus.COMPLETADO.value: frozenset(),
    TicketStatus.CERRADO.value: frozenset(),
}


class DuplicateSupportTicketError(ValueError):
    """El owner ya creo un ticket equivalente en las ultimas 24 horas."""


# ================================================================== #
# Servicio de use cases (AC-014-02, AC-014-05, AC-014-11)
# ================================================================== #


class SupportTicketService:
    """Casos de uso para soporte basico."""

    def __init__(self, repo: SupportTicketRepository) -> None:
        self.repo = repo

    async def create_ticket(
        self,
        title: str,
        description: str | None,
        category_id: int | None,
        owner_id: int,
        clinic_id: int,
    ) -> dict[str, Any]:
        """Crear un nuevo ticket asociado al owner y clinica autenticada.

        Valida longitud de titulo (min 5 chars) antes de llamar al repo.
        El estado inicia como 'iniciado' segun AC-014-03.
        """
        normalized_title = title.strip()
        if len(normalized_title) < 5:
            raise ValueError("El titulo del ticket debe tener al menos 5 caracteres")

        is_duplicate = await self.repo.find_recent_duplicate(
            title=normalized_title,
            owner_id=owner_id,
            clinic_id=clinic_id,
            created_since=datetime.now(UTC) - timedelta(hours=24),
        )
        if is_duplicate:
            raise DuplicateSupportTicketError(
                "Ya existe un ticket con el mismo titulo creado en las ultimas 24 horas"
            )

        domain, cat = await self.repo.create_ticket(
            title=normalized_title,
            description=description,
            category_id=category_id,
            owner_id=owner_id,
            clinic_id=clinic_id,
        )
        return {
            "id": domain.id,
            "title": domain.title,
            "description": domain.description,
            "status": domain.status,
            "category_id": domain.category_id,
            "category": {"id": cat.id, "name": cat.name} if cat else None,
            "owner_id": domain.owner_id,
            "clinic_id": domain.clinic_id,
            "created_at": (
                domain.created_at.isoformat()
                if isinstance(domain.created_at, datetime)
                else str(domain.created_at)
            ),
            "updated_at": (
                domain.updated_at.isoformat()
                if isinstance(domain.updated_at, datetime)
                else str(domain.updated_at)
            ),
        }

    async def list_for_user(
        self,
        owner_id: int,
        clinic_id: int,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Listar tickets del usuario autenticado. Filtra por tenant y opcionalmente por estado."""
        items, total = await self.repo.list_by_owner(
            owner_id, clinic_id, page, page_size, status
        )
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return {
            "items": [
                {
                    "id": t[0].id,
                    "title": t[0].title,
                    "status": t[0].status,
                    "category_name": t[1].name if t[1] else None,
                    "owner_id": t[0].owner_id,
                    "clinic_id": t[0].clinic_id,
                    "created_at": (
                        t[0].created_at.isoformat()
                        if isinstance(t[0].created_at, datetime)
                        else str(t[0].created_at)
                    ),
                    "updated_at": (
                        t[0].updated_at.isoformat()
                        if isinstance(t[0].updated_at, datetime)
                        else str(t[0].updated_at)
                    ),
                }
                for t in items
            ],
            "meta": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": pages,
            },
        }

    async def get_detail(
        self, ticket_id: int, owner_id: int, clinic_id: int
    ) -> dict[str, Any] | None:
        """Obtener detalle de un ticket. Retorna None si es ajeno a clinica/owner."""
        result = await self.repo.get_by_id_for_owner(ticket_id, owner_id, clinic_id)
        if result is None:
            return None
        t, cat = result
        return {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "category_id": t.category_id,
            "category": {"id": cat.id, "name": cat.name} if cat else None,
            "owner_id": t.owner_id,
            "clinic_id": t.clinic_id,
            "created_at": (
                t.created_at.isoformat()
                if isinstance(t.created_at, datetime)
                else str(t.created_at)
            ),
            "updated_at": (
                t.updated_at.isoformat()
                if isinstance(t.updated_at, datetime)
                else str(t.updated_at)
            ),
        }

    async def change_status(
        self,
        ticket_id: int,
        owner_id: int,
        clinic_id: int,
        new_status: str,
    ) -> dict[str, Any] | None:
        """Cambiar estado del ticket. Aplica reglas de transicion validas (AC-014-05)."""
        current = await self.repo.get_by_id_for_owner(ticket_id, owner_id, clinic_id)
        if current is None:
            return None
        old_status = current[0].status
        allowed = _TRANSITIONS.get(old_status, frozenset())
        if new_status not in allowed:
            raise ValueError(
                f"Transicion invalida de {old_status} a {new_status}. Transiciones permitidas: {'; '.join(sorted(allowed)) or 'ninguna'}"
            )

        result = await self.repo.update_status(
            ticket_id, owner_id, clinic_id, new_status
        )
        if result is None:
            return None
        _, received_new_status = result
        return {
            "ticket_id": ticket_id,
            "old_status": old_status,
            "new_status": received_new_status,
        }

    async def list_active_categories(self, clinic_id: int) -> list[dict[str, Any]]:
        """Listar categorias activas de una clinica."""
        cats = await self.repo.list_active_categories(clinic_id)
        return [{"id": c.id, "name": c.name} for c in cats]
