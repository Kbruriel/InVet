"""Routers de soporte basico (BE-014, AC-014-01 / 03 / 04 / 05).

Endpoints protegidos para gestion de tickets con guardas de autenticacion,
isolemento de tenant y reglas de transicion de estados.

Seguridad:
- Todos los endpoints requieren bearer jwt (AC-014-07).
- Operaciones solo acceden a data del tenant autenticado (AC-014-11).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.support_ticket_schemas import (
    TicketCreateRequest,
    TicketStatusChangeResponse,
    TicketStatusUpdateRequest,
)
from app.application.support_ticket_use_cases import (
    DuplicateSupportTicketError,
    SupportTicketService,
)
from app.core.security import get_current_access_user
from app.data.support_ticket_repo import get_support_ticket_repo
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/tickets", tags=["soporte"])


def _user_id(current_user: dict[str, Any]) -> int:
    uid = current_user.get("user_id") or current_user.get("id")
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado.",
        )
    return int(uid)


def _clinic_id(current_user: dict[str, Any]) -> int:
    cid = current_user.get("clinic_id") or current_user.get("tenant_id")
    if cid is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una clínica asociada.",
        )
    return int(cid)


def _service(db: Session = Depends(get_db)) -> SupportTicketService:
    return SupportTicketService(get_support_ticket_repo(db))


# ================================================================== #
# POST /api/v1/tickets (AC-014-01, AC-014-07)
# ================================================================== #


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: SupportTicketService = Depends(_service),
) -> dict[str, Any]:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)

    try:
        result = await svc.create_ticket(
            title=payload.title.strip(),
            description=payload.description,
            category_id=payload.category_id,
            owner_id=uid,
            clinic_id=cid,
        )
    except DuplicateSupportTicketError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return result


# ================================================================== #
# GET /api/v1/tickets (AC-014-03, AC-014-07)
# ================================================================== #


@router.get("")
async def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: SupportTicketService = Depends(_service),
) -> dict[str, Any]:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)

    result = await svc.list_for_user(uid, cid, page, page_size, status)
    return result


# ================================================================== #
# GET /api/v1/tickets/categories (AC-014-06, AC-014-07)
# ================================================================== #


@router.get("/categories")
async def list_categories(
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: SupportTicketService = Depends(_service),
) -> dict[str, Any]:
    cid = _clinic_id(current_user)

    categories = await svc.list_active_categories(cid)
    return {"items": categories}


# ================================================================== #
# GET /api/v1/tickets/{ticket_id} (AC-014-04, AC-014-06, AC-014-07)
# ================================================================== #


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: SupportTicketService = Depends(_service),
) -> dict[str, Any]:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)

    result = await svc.get_detail(ticket_id, uid, cid)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )
    return result


# ================================================================== #
# PATCH /api/v1/tickets/{ticket_id}/status (AC-014-05, AC-014-07)
# ================================================================== #


@router.patch("/{ticket_id}/status")
async def change_status(
    ticket_id: int,
    payload: TicketStatusUpdateRequest,
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: SupportTicketService = Depends(_service),
) -> TicketStatusChangeResponse:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)

    try:
        result = await svc.change_status(ticket_id, uid, cid, payload.new_status)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado o pertenece a otro usuario",
        )
    return result
