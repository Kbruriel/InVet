"""Casos de uso para notificaciones internas (lectura/marcacion/emision/listado)."""

from __future__ import annotations

import logging
from datetime import UTC
from datetime import datetime as _dt
from typing import Any

from pydantic import BaseModel, Field

from app.data.notification_repo import NotificationRepository
from app.domain.entities.notification import (
    EmailProvider,
    LoggingEmailSender,
    Notification,
    is_valid_event_type,
)

logger = logging.getLogger(__name__)


class NotificationRead(BaseModel):
    id: int
    clinic_id: int
    user_id: int | None = None
    event_type: str
    subject: str
    body: str
    ref_type: str | None = None
    ref_id: int | None = None
    is_read: bool
    read_at: str | None = Field(default=None, serialization_alias="readAt")
    created_at: str = Field(serialization_alias="createdAt")


class NotificationList(BaseModel):
    items: list[NotificationRead]
    meta: dict


class NotificationError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class NotificationService:
    """Casos de uso: listar/marcar-leer/emision/conteo."""

    def __init__(
        self, repo: NotificationRepository, email_provider: EmailProvider | None = None
    ) -> None:
        self.repo = repo
        self.email_provider = (
            email_provider if email_provider is not None else LoggingEmailSender()
        )

    async def list_for_user(
        self,
        user_id: int,
        clinic_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[NotificationRead], int]:
        items, total = await self.repo.list_by_user(
            user_id, clinic_id, page, page_size, unread_only
        )
        return [_to_read(n) for n in items], total

    async def emit(
        self,
        user_id: int | None,
        clinic_id: int,
        event_type: str,
        ref_type: str,
        ref_id: int,
        body_extra: str = "",
        recipient_email: str | None = None,
    ) -> dict[str, Any]:
        """Emitir una notificacion interna (dedup via repo)."""
        if user_id is None:
            return {"created": False, "email_sent": False, "reason": "user_id required"}
        if not is_valid_event_type(event_type):
            # Evento fuera del conjunto canonico: no insertar, no enviar, no propagar.
            logger.warning(
                "emit event_type no canonico: %s (ref_type=%s ref_id=%s)",
                event_type,
                ref_type,
                ref_id,
            )
            return {
                "created": False,
                "email_sent": False,
                "reason": "invalid_event_type",
            }
        existing = await self.repo.get_notification_for_user_key(
            user_id=user_id,
            event_type=event_type,
            ref_type=ref_type,
            ref_id=ref_id,
        )
        if existing is not None:
            return {"created": False, "email_sent": False, "reason": "already_exists"}
        notif = await self.repo.create_if_unique(
            clinic_id=clinic_id,
            user_id=user_id,
            event_type=event_type,
            subject="Notificacion " + event_type,
            body=(ref_type + "/" + str(ref_id) + " - " + body_extra).rstrip(),
            ref_type=ref_type,
            ref_id=ref_id,
        )
        if notif is None:
            return {"created": False, "email_sent": False, "reason": "already_exists"}
        email_sent = await self._send_email_stub(notif, recipient_email)
        return {"created": True, "email_sent": email_sent}

    async def _send_email_stub(
        self, notif: Notification, recipient_email: str | None
    ) -> bool:
        if recipient_email is None or not recipient_email:
            return False
        try:
            await self.email_provider.send(recipient_email, notif.subject, notif.body)
            return True
        except Exception:
            logger.warning(
                "fallo email_provider en emision de notificacion id=%s",
                notif.id,
                exc_info=True,
            )
            return False

    async def get_by_id(
        self, notification_id: int, user_id: int
    ) -> NotificationRead | None:
        n = await self.repo.get_by_id_for_user(notification_id, user_id)
        return _to_read(n) if n else None

    async def mark_as_read(
        self, notification_id: int, user_id: int
    ) -> NotificationRead | None:
        n = await self.repo.mark_read(notification_id, user_id)
        return _to_read(n) if n else None

    async def mark_all_as_read(self, user_id: int, clinic_id: int) -> int:
        return await self.repo.mark_all_read(user_id, clinic_id)

    async def count_unread(self, user_id: int, clinic_id: int) -> int:
        return await self.repo.count_unread(user_id, clinic_id)


def _to_read(n: Notification) -> NotificationRead:
    cat = n.created_at or _dt.now(UTC)
    if not hasattr(cat, "isoformat"):
        cat = _dt.fromisoformat(str(cat)) if isinstance(cat, str) else cat
    rad = n.read_at
    read_str: str | None = (
        rad.isoformat()
        if rad is not None and hasattr(rad, "isoformat")
        else str(rad) if rad else None
    )
    return NotificationRead(
        id=n.id or 0,
        clinic_id=n.clinic_id or 0,
        user_id=n.user_id,
        event_type=str(n.event_type),
        subject=str(n.subject),
        body=str(n.body),
        ref_type=n.ref_type,
        ref_id=n.ref_id,
        is_read=bool(n.is_read),
        read_at=read_str,
        created_at=cat.isoformat(),
    )
