"""Tests unitarios para caso de uso de notificaciones con funcionalidad de email."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.notification_use_cases import NotificationService
from app.data.notification_repo import NotificationRepository
from app.domain.entities.notification import LoggingEmailSender, Notification


@pytest.fixture
def mock_notification_repo():
    """Fixture para repo de notificaciones."""
    return AsyncMock(spec=NotificationRepository)


@pytest.fixture
def mock_email_provider():
    """Fixture para proveedor de email mockeado."""
    provider = AsyncMock()
    provider.send = AsyncMock(return_value=None)
    return provider


@pytest.fixture
def notification_service(mock_notification_repo, mock_email_provider):
    """Fixture para NotificationService con repo y proveedor mockeados."""
    return NotificationService(mock_notification_repo, mock_email_provider)


@pytest.mark.asyncio
async def test_emit_creates_notification_and_sends_email_once(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: emit() crea notificacion y envia email una vez si hay destinatario."""
    # Simulamos que no existe la notificacion para no entrar en el path de dedup
    mock_notification_repo.get_notification_for_user_key = AsyncMock(return_value=None)

    # Simulamos un resultado exitoso de create_if_unique (notifica que se creó)
    fake_notification = MagicMock(spec=Notification)
    fake_notification.id = 1
    fake_notification.subject = "Notificacion appointment_created"
    fake_notification.body = "appointment/1 - Mascota: gato"
    mock_notification_repo.create_if_unique = AsyncMock(return_value=fake_notification)

    # Ejecutamos
    result = await notification_service.emit(
        user_id=1,
        clinic_id=1,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        body_extra="Mascota: gato",
        recipient_email="owner@example.com",
    )

    # Verificamos que el repo fue llamado
    mock_notification_repo.create_if_unique.assert_called_once()

    # Verificamos que el provider envio email (no se lanzo excepcion)
    assert result["created"] is True
    assert result["email_sent"] is True
    mock_email_provider.send.assert_called_once_with(
        "owner@example.com",
        "Notificacion appointment_created",
        "appointment/1 - Mascota: gato",
    )


@pytest.mark.asyncio
async def test_emit_dedup_second_call_no_row_no_email(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: emit() no crea notificacion ni envia email si ya existe."""
    # Simulamos que ya existe el registro
    mock_notification_repo.get_notification_for_user_key = AsyncMock(
        return_value=MagicMock()
    )

    result = await notification_service.emit(
        user_id=1,
        clinic_id=1,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        body_extra="Mascota: gato",
        recipient_email="owner@example.com",
    )

    # Verificamos que el repo de notificaciones no se llamo para crear
    mock_notification_repo.create_if_unique.assert_not_called()
    mock_email_provider.send.assert_not_called()

    assert result["created"] is False
    assert result["email_sent"] is False
    assert result["reason"] == "already_exists"


@pytest.mark.asyncio
async def test_emit_provider_exception_does_not_propagate(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: si el provider lanza excepcion, la notificacion se crea pero email falla."""
    # Simulamos que no existe
    mock_notification_repo.get_notification_for_user_key = AsyncMock(return_value=None)

    fake_notification = MagicMock(spec=Notification)
    fake_notification.id = 1
    fake_notification.subject = "Notificacion appointment_created"
    fake_notification.body = "appointment/1 - Mascota: gato"
    mock_notification_repo.create_if_unique = AsyncMock(return_value=fake_notification)

    # Simulamos que el provider lanza una excepcion
    mock_email_provider.send = AsyncMock(side_effect=Exception("Error de envio"))

    result = await notification_service.emit(
        user_id=1,
        clinic_id=1,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        body_extra="Mascota: gato",
        recipient_email="owner@example.com",
    )

    # El resultado muestra que la notificacion se creo
    assert result["created"] is True
    assert result["email_sent"] is False
    mock_email_provider.send.assert_called_once()


@pytest.mark.asyncio
async def test_emit_without_recipient_email_skips_send(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: emit() sin email destinatario no intenta enviar email."""
    # Simulamos que no existe
    mock_notification_repo.get_notification_for_user_key = AsyncMock(return_value=None)

    fake_notification = MagicMock(spec=Notification)
    fake_notification.id = 1
    fake_notification.subject = "Notificacion appointment_created"
    fake_notification.body = "appointment/1 - Mascota: gato"
    mock_notification_repo.create_if_unique = AsyncMock(return_value=fake_notification)

    # Pasamos None como email destinatario
    result = await notification_service.emit(
        user_id=1,
        clinic_id=1,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        body_extra="Mascota: gato",
        recipient_email=None,  # No hay email
    )

    # Verificamos que el proveedor no se llamo y la notificacion se creo
    assert result["created"] is True
    assert result["email_sent"] is False
    mock_email_provider.send.assert_not_called()


@pytest.mark.asyncio
async def test_emit_none_user_no_send(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: emit() con user_id None no crea notificacion ni envia email."""
    # Llamamos sin id de usuario - se debe rechazar
    result = await notification_service.emit(
        user_id=None,
        clinic_id=1,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=1,
        body_extra="Mascota: gato",
        recipient_email="owner@example.com",
    )

    assert result["created"] is False
    assert result["email_sent"] is False
    assert result["reason"] == "user_id required"
    mock_notification_repo.create_if_unique.assert_not_called()
    mock_email_provider.send.assert_not_called()


@pytest.mark.asyncio
async def test_emit_event_type_not_in_canonical_set_rejected(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: emit() rechaza event_type que no esta en el enum canonico (validacion T06)."""
    result = await notification_service.emit(
        user_id=1,
        clinic_id=1,
        event_type="EVENTO_INVENCIDO",
        ref_type="appointment",
        ref_id=1,
        body_extra="Mascota: gato",
        recipient_email="owner@example.com",
    )
    assert result["created"] is False
    assert result["email_sent"] is False
    assert result["reason"] == "invalid_event_type"
    mock_notification_repo.create_if_unique.assert_not_called()
    mock_email_provider.send.assert_not_called()


@pytest.mark.asyncio
async def test_emit_all_canonical_event_types_accept(
    notification_service: NotificationService,
    mock_notification_repo: NotificationRepository,
    mock_email_provider,
):
    """Test: todos los valores del enum canonico son aceptados por emit()."""
    from app.domain.entities.notification import VALID_EVENT_TYPES

    assert len(VALID_EVENT_TYPES) == 10
    for i, event in enumerate(sorted(VALID_EVENT_TYPES)):
        mock_notification_repo.get_notification_for_user_key = AsyncMock(
            return_value=None
        )
        fake = MagicMock(spec=Notification)
        fake.id = i
        fake.subject = "S"
        fake.body = "B"
        mock_notification_repo.create_if_unique = AsyncMock(return_value=fake)
        result = await notification_service.emit(
            user_id=1,
            clinic_id=1,
            event_type=event,
            ref_type="appointment",
            ref_id=i,
            body_extra="",
            recipient_email=None,
        )
        assert result["created"] is True


def test_init_with_default_logging_provider():
    """Test: el servicio se inicializa con LoggingEmailSender si no se pasa uno."""
    # No pasamos provider, debe usar LoggingEmailSender por defecto
    repo = MagicMock()
    service = NotificationService(repo)

    # Verificamos que tenga un proveedor que sea de tipo LoggingEmailSender
    assert isinstance(service.email_provider, LoggingEmailSender)
