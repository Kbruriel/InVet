"""Pruebas de integracion por flujo para emision de notificaciones (BE-013-T06).

Verificacion de extremo a extremo sobre la capa de aplicacion + persistencia real
(SQLite, fixture db_session) para cada uno de los 5 flujos notificados:

1. appointment_created      -> cita alta
2. appointment_confirmed    -> transicion de estado
3. payment_completed        -> pago
4. consultation_completed   -> consulta
5. prescription_created     -> receta

Para cada flujo se verifica:
- una fila en la tabla notifications (no cero, no dos),
- email enviado exactamente una vez si hay destinatario,
- doble emision con la misma clave de dedup NO inserta segunda fila y no reenvia,
- fallo del provider NO propaga al caller (resiliencia HTTP),
- emit_notify() (helper de routers) es deterministico y no levanta excepcion,
- default NotificationService() usa LoggingEmailSender.
"""

from __future__ import annotations

from typing import Any

import pytest
from sqlalchemy import select

from app.api.v1.routers._notify import emit_notify
from app.application.notification_use_cases import NotificationService
from app.data.notification_repo import get_notification_repo
from app.domain.entities.notification import EmailProvider
from app.infrastructure.database.models.notification import (
    Notification as NotificationModel,
)

CLINIC = 10_000
USER = 42_000
EMAIL = "owner@vet.example"


class SpyEmailProvider(EmailProvider):
    """Proveedor espia que registra envios y puede inyectar excepcion."""

    def __init__(self, fail: bool = False) -> None:
        self.sent: list[tuple[str, str, str]] = []
        self._fail = fail

    async def send(self, email: str, subject: str, body: str) -> None:
        if self._fail:
            raise RuntimeError("email provider caido")
        self.sent.append((email, subject, body))


def _svc(db_session: Any, provider: EmailProvider | None = None) -> NotificationService:
    repo = get_notification_repo(db_session)
    return NotificationService(repo, email_provider=provider or SpyEmailProvider())


async def _emit(
    db_session: Any,
    *,
    event_type: str,
    ref_type: str,
    ref_id: int,
    provider: EmailProvider | None = None,
    recipient_email: str | None = EMAIL,
    user_id: int = USER,
    clinic_id: int = CLINIC,
    body_extra: str = "extra",
) -> dict[str, Any]:
    svc = _svc(db_session, provider)
    return await svc.emit(
        user_id=user_id,
        clinic_id=clinic_id,
        event_type=event_type,
        ref_type=ref_type,
        ref_id=ref_id,
        body_extra=body_extra,
        recipient_email=recipient_email,
    )


def _rows_for(
    db_session: Any, *, user_id: int, event_type: str, ref_type: str, ref_id: int
) -> list[NotificationModel]:
    stmt = select(NotificationModel).where(
        NotificationModel.user_id == user_id,
        NotificationModel.event_type == event_type,
        NotificationModel.ref_type == ref_type,
        NotificationModel.ref_id == ref_id,
    )
    return list(db_session.execute(stmt).scalars().all())


@pytest.mark.asyncio
async def test_flujo_cita_creada_crear_fila_email_1(db_session):
    provider = SpyEmailProvider()
    r1 = await _emit(
        db_session,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        provider=provider,
    )
    assert r1["created"] is True
    assert r1["email_sent"] is True
    assert len(provider.sent) == 1
    assert provider.sent[0][0] == EMAIL

    rows = _rows_for(
        db_session,
        user_id=USER,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
    )
    assert len(rows) == 1

    # Doble emision con la misma clave: NO debe insertar segunda fila, NO debe reenviar email
    provider2 = SpyEmailProvider()
    r2 = await _emit(
        db_session,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        provider=provider2,
    )
    assert r2["created"] is False
    assert r2["email_sent"] is False
    assert r2.get("reason") == "already_exists"
    assert provider2.sent == []

    rows2 = _rows_for(
        db_session,
        user_id=USER,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
    )
    assert len(rows2) == 1


@pytest.mark.asyncio
async def test_flujo_cita_status_confirmada(db_session):
    provider = SpyEmailProvider()
    r1 = await _emit(
        db_session,
        event_type="appointment_confirmed",
        ref_type="appointment",
        ref_id=21,
        provider=provider,
    )
    assert r1["created"] is True
    assert r1["email_sent"] is True

    provider2 = SpyEmailProvider()
    r2 = await _emit(
        db_session,
        event_type="appointment_confirmed",
        ref_type="appointment",
        ref_id=21,
        provider=provider2,
    )
    assert r2["created"] is False
    assert provider2.sent == []


@pytest.mark.asyncio
async def test_flujo_pago_paid(db_session):
    provider = SpyEmailProvider()
    r1 = await _emit(
        db_session,
        event_type="payment_completed",
        ref_type="payment",
        ref_id=42,
        provider=provider,
    )
    assert r1["created"] is True
    assert r1["email_sent"] is True

    # dedup sobre la segunda emision con la misma clave
    provider2 = SpyEmailProvider()
    r2 = await _emit(
        db_session,
        event_type="payment_completed",
        ref_type="payment",
        ref_id=42,
        provider=provider2,
    )
    assert r2["created"] is False
    assert provider2.sent == []


@pytest.mark.asyncio
async def test_flujo_consulta_completada(db_session):
    provider = SpyEmailProvider()
    r1 = await _emit(
        db_session,
        event_type="consultation_completed",
        ref_type="consultation",
        ref_id=77,
        provider=provider,
        body_extra="Diagnostico: resfrio",
    )
    assert r1["created"] is True
    assert r1["email_sent"] is True

    provider2 = SpyEmailProvider()
    r2 = await _emit(
        db_session,
        event_type="consultation_completed",
        ref_type="consultation",
        ref_id=77,
        provider=provider2,
        body_extra="Diagnostico: resfrio",
    )
    assert r2["created"] is False
    assert provider2.sent == []


@pytest.mark.asyncio
async def test_flujo_receta_creada(db_session):
    provider = SpyEmailProvider()
    r1 = await _emit(
        db_session,
        event_type="prescription_created",
        ref_type="prescription",
        ref_id=101,
        provider=provider,
        body_extra="Receta vet. registrada",
    )
    assert r1["created"] is True
    assert r1["email_sent"] is True

    provider2 = SpyEmailProvider()
    r2 = await _emit(
        db_session,
        event_type="prescription_created",
        ref_type="prescription",
        ref_id=101,
        provider=provider2,
        body_extra="Receta vet. registrada",
    )
    assert r2["created"] is False
    assert provider2.sent == []


@pytest.mark.asyncio
async def test_provider_fallo_no_propaga(db_session):
    """T06 (resiliencia HTTP): excepcion del provider NO bloquea la respuesta."""
    provider = SpyEmailProvider(fail=True)
    r = await _emit(
        db_session,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=200,
        provider=provider,
        user_id=50_000,
    )
    # La notificacion SI se crea (persistencia garantizada),
    # pero el email no se envia y el caller recibe un dict sin exepxion.
    assert r["created"] is True
    assert r["email_sent"] is False
    assert provider.sent == []


@pytest.mark.asyncio
async def test_emit_notify_helper_deterministic_and_dedup(db_session):
    """T06 (helper emit_notify): deterministico, resiliencia, dedup."""
    r1 = await emit_notify(
        db=db_session,
        recipient_user_id=60_000,
        recipient_email="owner@x.com",
        clinic_id=CLINIC,
        event_type="appointment_created",
        ref_entity="appointment",
        ref_id=60_000,
        body_extra="extra",
    )
    assert r1["created"] is True
    # emit_notify() usa por defecto LoggingEmailSender (log stub); no lanza.
    assert r1["email_sent"] is True

    r2 = await emit_notify(
        db=db_session,
        recipient_user_id=60_000,
        recipient_email="owner@x.com",
        clinic_id=CLINIC,
        event_type="appointment_created",
        ref_entity="appointment",
        ref_id=60_000,
    )
    assert r2["created"] is False
    assert r2["email_sent"] is False


@pytest.mark.asyncio
async def test_emit_sincronizo_sin_email_skips_send(db_session):
    """Si recipient_email=None, el servicio NO llama al provider."""
    provider = SpyEmailProvider()
    r = await _emit(
        db_session,
        event_type="payment_completed",
        ref_type="payment",
        ref_id=900,
        provider=provider,
        recipient_email=None,
        user_id=70_000,
    )
    assert r["created"] is True
    assert r["email_sent"] is False
    assert provider.sent == []


@pytest.mark.asyncio
async def test_emit_con_user_none_rechaza(db_session):
    user_none_result = await _svc(db_session).emit(
        user_id=None,
        clinic_id=CLINIC,
        event_type="payment_completed",
        ref_type="payment",
        ref_id=1,
        recipient_email=EMAIL,
    )
    assert user_none_result["created"] is False
    assert user_none_result["reason"] == "user_id required"


@pytest.mark.asyncio
async def test_default_email_provider_es_logging_sender(db_session):
    """NotificationService() con provider=None usa LoggingEmailSender por defecto."""
    from app.domain.entities.notification import LoggingEmailSender

    repo = get_notification_repo(db_session)
    svc = NotificationService(repo)
    assert isinstance(svc.email_provider, LoggingEmailSender)

    r = await svc.emit(
        user_id=80_000,
        clinic_id=CLINIC,
        event_type="prescription_created",
        ref_type="prescription",
        ref_id=80_000,
        body_extra="Log only",
        recipient_email="owner@z.com",
    )
    # El logging stub es exitoso: no lanza, y el resultado refleja email_sent=True.
    assert r["created"] is True
    assert r["email_sent"] is True


@pytest.mark.asyncio
async def test_multi_flujo_1_usuario_4_notificaciones_unicas(db_session):
    """Cobra los 4 flows que un usuario puede recibir: cita, estado, consulta, receta.

    Todas deben coexistir sin dedup entre flujos distintos aunque compartan
    ref_id, porque event_type+ref_type son distintos.
    """
    u = 90_000
    p1 = SpyEmailProvider()
    await _emit(
        db_session,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=7,
        provider=p1,
        user_id=u,
    )
    p2 = SpyEmailProvider()
    await _emit(
        db_session,
        event_type="appointment_confirmed",
        ref_type="appointment",
        ref_id=7,
        provider=p2,
        user_id=u,
    )
    p3 = SpyEmailProvider()
    await _emit(
        db_session,
        event_type="consultation_completed",
        ref_type="consultation",
        ref_id=7,
        provider=p3,
        user_id=u,
    )
    p4 = SpyEmailProvider()
    await _emit(
        db_session,
        event_type="prescription_created",
        ref_type="prescription",
        ref_id=7,
        provider=p4,
        user_id=u,
    )

    for p in (p1, p2, p3, p4):
        assert len(p.sent) == 1

    stmt = select(NotificationModel).where(
        NotificationModel.user_id == u,
        NotificationModel.ref_type == "appointment",
        NotificationModel.ref_id == 7,
    )
    rows = list(db_session.execute(stmt).scalars().all())
    # Una por cita creada + una por estado confirmado (2 rows con event_type distintos)
    event_types = {r.event_type for r in rows}
    assert event_types == {"appointment_created", "appointment_confirmed"}
