"""Router de notificaciones internas (BE-013).

Endpoints de recepcion/lectura de notificaciones del usuario autenticado.
La EMISION de notificaciones es in-proceso (see ``app.api.v1.routers._notify``)
y NO se expone como endpoint HTTP: evitar que cualquier usuario autenticado
pueda emitir notificaciones contra un ``user_id``/``clinic_id`` arbitrario (IDOR).

Seguridad:
- 401 si el token no expone el identificador de usuario.
- 403 si el usuario no tiene clinica asociada (aislamiento de tenant).
- Aislamiento por (user_id, clinic_id) en todas las consultas (BOLA).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.notification_use_cases import (
    NotificationList,
    NotificationRead,
    NotificationService,
)
from app.core.security import get_current_access_user
from app.data.notification_repo import get_notification_repo
from app.infrastructure.database.session import get_db

router = APIRouter(prefix="/notifications", tags=["notificaciones"])


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


def _service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(get_notification_repo(db))


@router.get("", response_model=NotificationList)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: NotificationService = Depends(_service),
) -> NotificationList:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)
    items, total = await svc.list_for_user(uid, cid, page, page_size, unread_only)
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return NotificationList(
        items=items,
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": pages,
            "unread_only": unread_only,
        },
    )


@router.get("/count/unread", response_model=dict)
async def count_unread(
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: NotificationService = Depends(_service),
) -> dict:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)
    count = await svc.count_unread(uid, cid)
    return {"unread": count}


@router.post("/read-all", response_model=dict)
async def mark_all_read(
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: NotificationService = Depends(_service),
) -> dict:
    uid = _user_id(current_user)
    cid = _clinic_id(current_user)
    count = await svc.mark_all_as_read(uid, cid)
    return {"read": count}


@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: int,
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: NotificationService = Depends(_service),
) -> NotificationRead:
    uid = _user_id(current_user)
    result = await svc.get_by_id(notification_id, uid)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacion no encontrada",
        )
    return result


@router.patch("/{notification_id}", response_model=NotificationRead)
async def mark_as_read(
    notification_id: int,
    current_user: dict[str, Any] = Depends(get_current_access_user),
    svc: NotificationService = Depends(_service),
) -> NotificationRead:
    uid = _user_id(current_user)
    result = await svc.mark_as_read(notification_id, uid)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificacion no encontrada o pertenece a otro usuario",
        )
    return result
