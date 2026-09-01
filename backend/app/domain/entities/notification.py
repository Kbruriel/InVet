"""Entidad de dominio para notificaciones internas y proveedor de correo abstracto (BE-013)."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class NotificationEventType(Enum):
    """Tipos de evento canonicos que generan notificaciones internas (BE-013-T06).

    El plan original declaraba 5 valores genericos (APPOINTMENT_CREATED,
    APPOINTMENT_STATUS_CHANGED, CONSULTATION_STATUS_CHANGED, PRESCRIPTION_ISSUED,
    PAYMENT_RECEIVED). La implementacion de los flujos (citas, consultas, recetas,
    pagos) emite eventos granulares en snake_case; esta lista CANONICA agrupa
    ambos conjuntos: la semantica del plan de 5 eventos cubre los granulares
    (p. ej. APPOINTMENT_STATUS_CHANGED -> appointment_confirmed/cancelled/...).
    """

    APPOINTMENT_CREATED = "appointment_created"
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_COMPLETED = "appointment_completed"
    APPOINTMENT_NO_SHOW = "appointment_no_show"
    APPOINTMENT_APPROVED = "appointment_approved"
    CONSULTATION_COMPLETED = "consultation_completed"
    PRESCRIPTION_CREATED = "prescription_created"
    PAYMENT_COMPLETED = "payment_completed"
    PAYMENT_CANCELLED = "payment_cancelled"


VALID_EVENT_TYPES: frozenset[str] = frozenset(e.value for e in NotificationEventType)


def is_valid_event_type(event_type: str) -> bool:
    """Verificar que un evento de emision pertenece al conjunto canonico."""
    return event_type in VALID_EVENT_TYPES


class Notification:
    """Entidad de dominio para una notificacion interna."""

    def __init__(
        self,
        id: int | None = None,
        clinic_id: int | None = None,
        user_id: int | None = None,
        event_type: str | None = None,
        subject: str = "",
        body: str = "",
        ref_type: str | None = None,
        ref_id: Any | None = None,
        is_read: bool = False,
        read_at: datetime | None = None,
        created_at: datetime | None = None,
    ):
        self.id = id
        self.clinic_id = clinic_id
        self.user_id = user_id
        self.event_type = event_type
        self.subject = subject[:2048]
        self.body = body[:2048]
        self.ref_type = ref_type
        self.ref_id = ref_id
        self.is_read = is_read
        self.read_at = read_at
        self.created_at = created_at or datetime.now(UTC)


class EmailProvider(ABC):
    """Puerto abstracto para envio de correos electronicos."""

    @abstractmethod
    async def send(self, email: str, subject: str, body: str) -> None:
        """Enviar un correo electronico al destinatario especificado."""
        ...


class LoggingEmailSender(EmailProvider):
    """Stub MVP que loguea el envio sin transmitir por red.

    Escribe recipient, subject y provider en logger.info sin exponer
    datos sensibles del negocio ni enviar correos reales.
    """

    PROVIDER_NAME = "logging_stub"

    async def send(self, email: str, subject: str, body: str) -> None:
        """Loguea metadata del correo sin enviar ni exponer datos sensibles."""
        logger.info(
            "email_stub recipient=%s subject=%s provider=%s",
            email,
            subject,
            self.PROVIDER_NAME,
        )
