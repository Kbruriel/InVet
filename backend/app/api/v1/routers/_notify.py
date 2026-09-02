"""Helper para emitir notificaciones automaticas desde flujos MVP (BE-013-T06).

Exponer `emit_notify()` que puede ser llamada con asyncio.create_task() desde
cualquier router sin bloquear la respuesta HTTP.

Uso:
    from app.api.v1.routers._notify import emit_notify

    # dentro del endpoint POST/PUT despues de persistir:
    asyncio.create_task(
        emit_notify(db, sender_user_id=cuser["user_id"], recipient_type="owner",
                     ref_entity="appointment", ref_id=appointment.id,
                     event_type="appointment_created", body_extra=f"Mascota: {pet_name}")
    )
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session


async def emit_notify(
    db: Session,
    *,
    recipient_user_id: int,
    recipient_email: str | None,
    clinic_id: int,
    event_type: str,
    ref_entity: str,
    ref_id: int,
    body_extra: str = "",
) -> dict[str, Any]:
    """Enviar notificacion sin bloquear la respuesta.

    Nota: usar await directamente en el endpoint, no asyncio.create_task(),
    para evitar fallo en persistencia o pruebas desconfiables.
    """
    from app.application.notification_use_cases import NotificationService
    from app.data.notification_repo import get_notification_repo

    svc = NotificationService(get_notification_repo(db))
    try:
        return await svc.emit(
            user_id=recipient_user_id,
            recipient_email=recipient_email,
            clinic_id=clinic_id,
            event_type=event_type,
            ref_type=ref_entity,
            ref_id=ref_id,
            body_extra=body_extra,
        )
    except Exception:
        # No bloquear caller si falla (email provider mock, dedup, etc.)
        return {"created": False, "email_sent": False, "reason": "emission_failed"}
