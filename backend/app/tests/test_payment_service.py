"""Pruebas de casos de uso de pagos operativos (BE-011-T04)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.domain.entities.appointment import Appointment, AppointmentStatus, AppointmentType
from app.domain.entities.payment import Payment, PaymentCreate, PaymentMethod, PaymentStatus
from app.domain.entities.service import Service
from app.services.payment_service import (
    AlreadyCancelledError,
    AppointmentNotFoundError,
    CancelPaymentUseCase,
    CreatePaymentUseCase,
    InvalidCashPaymentError,
    PaymentNotFoundError,
    PaymentService,
    ServiceInactiveError,
    ServiceNotFoundError,
    compute_change_amount,
)


CLINIC = 1


def _appointment(overrides=None):
    data = {
        "id": 1,
        "owner_id": 1,
        "pet_id": 1,
        "clinic_id": CLINIC,
        "branch_id": 1,
        "appointment_type": AppointmentType.CONSULTATION,
        "status": AppointmentStatus.PENDING,
        "scheduled_start": datetime.now(UTC),
        "scheduled_end": datetime.now(UTC) + timedelta(minutes=30),
    }
    if overrides:
        data.update(overrides)
    return Appointment(**data)


def _service(overrides=None):
    data = {
        "id": 1,
        "clinic_id": CLINIC,
        "name": "Consulta",
        "price": 100.0,
        "duration_minutes": 30,
        "is_active": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    if overrides:
        data.update(overrides)
    return Service(**data)


def _payment(overrides=None):
    data = {
        "id": 100,
        "appointment_id": 1,
        "service_id": 1,
        "clinic_id": CLINIC,
        "amount": 10_000,
        "method": PaymentMethod.CASH,
        "amount_received": 10_000,
        "change_amount": 0,
        "status": PaymentStatus.PAID,
        "paid_at": datetime.now(UTC),
    }
    if overrides:
        data.update(overrides)
    return Payment(**data)


def _create_data(overrides=None):
    data = {
        "appointment_id": 1,
        "service_id": 1,
        "amount": 10_000,
        "method": PaymentMethod.CASH,
        "amount_received": 10_000,
        "created_by": 7,
    }
    if overrides:
        data.update(overrides)
    return PaymentCreate(**data)


@pytest.fixture
def payment_repo():
    return AsyncMock()


@pytest.fixture
def appointment_repo():
    return AsyncMock()


@pytest.fixture
def service_repo():
    return AsyncMock()


@pytest.fixture
def create_uc(payment_repo, appointment_repo, service_repo):
    return CreatePaymentUseCase(
        payment_repository=payment_repo,
        appointment_repository=appointment_repo,
        service_repository=service_repo,
    )


@pytest.fixture
def cancel_uc(payment_repo):
    return CancelPaymentUseCase(payment_repository=payment_repo)


@pytest.fixture
def service(payment_repo, appointment_repo, service_repo):
    return PaymentService(
        payment_repository=payment_repo,
        appointment_repository=appointment_repo,
        service_repository=service_repo,
    )


# ---------------------------------------------------------------------------
# compute_change_amount (regla de cambio por metodo CASH)
# ---------------------------------------------------------------------------


def test_compute_change_cash_returns_surplus():
    assert compute_change_amount(PaymentMethod.CASH, 10_000, 10_000) == 0
    assert compute_change_amount(PaymentMethod.CASH, 10_000, 20_000) == 10_000


def test_compute_change_non_cash_returns_none_even_with_surplus():
    assert compute_change_amount(PaymentMethod.CARD, 10_000, 10_000) is None
    assert compute_change_amount(PaymentMethod.TRANSFER, 10_000, 999_999) is None
    assert compute_change_amount(PaymentMethod.OTHER, 1, 1) is None


def test_compute_change_cash_without_received_raises():
    with pytest.raises(InvalidCashPaymentError):
        compute_change_amount(PaymentMethod.CASH, 10_000, None)


def test_compute_change_cash_shortfall_raises():
    with pytest.raises(InvalidCashPaymentError):
        compute_change_amount(PaymentMethod.CASH, 10_000, 5_000)


def test_compute_change_error_has_422_status():
    with pytest.raises(InvalidCashPaymentError) as exc:
        compute_change_amount(PaymentMethod.CASH, 10, 5)
    assert exc.value.status_code == 422


# ---------------------------------------------------------------------------
# CreatePaymentUseCase
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_payment_success_cash(payment_repo, appointment_repo, service_repo, create_uc):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = _service()
    payment_repo.create.return_value = _payment()

    result = await create_uc.execute(
        CLINIC,
        _create_data(overrides={"amount": 10_000, "amount_received": 12_500}),
    )

    assert result.id == 100
    assert result.status == PaymentStatus.PAID
    payment_repo.create.assert_awaited_once()
    sent = payment_repo.create.await_args.args[0]
    assert sent.change_amount == 2_500
    assert sent.status == PaymentStatus.PAID
    assert sent.clinic_id == CLINIC


@pytest.mark.asyncio
async def test_create_payment_non_cash_no_change(payment_repo, appointment_repo, service_repo, create_uc):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = _service()
    payment_repo.create.return_value = _payment(
        overrides={"method": PaymentMethod.CARD, "amount_received": None, "change_amount": None},
    )

    await create_uc.execute(
        CLINIC,
        _create_data(overrides={"method": PaymentMethod.CARD, "amount_received": None}),
    )

    sent = payment_repo.create.await_args.args[0]
    assert sent.method == PaymentMethod.CARD
    assert sent.change_amount is None
    assert sent.amount_received is None


@pytest.mark.asyncio
async def test_create_payment_appointment_missing(payment_repo, appointment_repo, create_uc):
    appointment_repo.get_by_id.return_value = None

    with pytest.raises(AppointmentNotFoundError) as exc:
        await create_uc.execute(CLINIC, _create_data())

    assert exc.value.status_code == 404
    payment_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_payment_service_missing(payment_repo, appointment_repo, service_repo, create_uc):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = None

    with pytest.raises(ServiceNotFoundError) as exc:
        await create_uc.execute(CLINIC, _create_data())

    assert exc.value.status_code == 422
    payment_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_payment_service_inactive(payment_repo, appointment_repo, service_repo, create_uc):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = _service(overrides={"is_active": False})

    with pytest.raises(ServiceInactiveError):
        await create_uc.execute(CLINIC, _create_data())

    payment_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_payment_cash_shortfall(payment_repo, appointment_repo, service_repo, create_uc):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = _service()

    with pytest.raises(InvalidCashPaymentError):
        await create_uc.execute(
            CLINIC,
            _create_data(
                overrides={
                    "method": PaymentMethod.CASH,
                    "amount": 10_000,
                    "amount_received": 7_500,
                }
            ),
        )

    payment_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_payment_cash_without_received(payment_repo, appointment_repo, service_repo, create_uc):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = _service()

    with pytest.raises(InvalidCashPaymentError):
        await create_uc.execute(
            CLINIC,
            _create_data(
                overrides={
                    "method": PaymentMethod.CASH,
                    "amount": 10_000,
                    "amount_received": None,
                }
            ),
        )

    payment_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_payment_tenant_isolation_passed_to_repos(
    payment_repo, appointment_repo, service_repo, create_uc
):
    appointment_repo.get_by_id.return_value = _appointment()
    service_repo.get_service_by_id.return_value = _service()
    payment_repo.create.return_value = _payment()

    tenant = 999
    await create_uc.execute(tenant, _create_data())

    appointment_repo.get_by_id.assert_awaited_once_with(1, tenant)
    service_repo.get_service_by_id.assert_awaited_once_with(1, tenant)
    sent = payment_repo.create.await_args.args[0]
    assert sent.clinic_id == tenant


# ---------------------------------------------------------------------------
# CancelPaymentUseCase
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_payment_success(payment_repo, cancel_uc):
    payment_repo.get_by_id.return_value = _payment()
    cancelled = _payment(
        overrides={"status": PaymentStatus.CANCELLED, "cancelled_at": datetime.now(UTC)},
    )
    payment_repo.cancel.return_value = cancelled

    result = await cancel_uc.execute(100, CLINIC)

    assert result.status == PaymentStatus.CANCELLED
    assert result.cancelled_at is not None
    payment_repo.cancel.assert_awaited_once_with(100, CLINIC)


@pytest.mark.asyncio
async def test_cancel_payment_not_found(payment_repo, cancel_uc):
    payment_repo.get_by_id.return_value = None

    with pytest.raises(PaymentNotFoundError) as exc:
        await cancel_uc.execute(9999, CLINIC)

    assert exc.value.status_code == 404
    payment_repo.cancel.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_already_cancelled_raises_409(payment_repo, cancel_uc):
    payment_repo.get_by_id.return_value = _payment(
        overrides={"status": PaymentStatus.CANCELLED, "cancelled_at": datetime.now(UTC)},
    )

    with pytest.raises(AlreadyCancelledError) as exc:
        await cancel_uc.execute(100, CLINIC)

    assert exc.value.status_code == 409
    payment_repo.cancel.assert_not_awaited()


# ---------------------------------------------------------------------------
# PaymentService (fachada)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_service_get_payment_found(payment_repo, service):
    payment_repo.get_by_id.return_value = _payment()

    result = await service.get_payment(100, CLINIC)

    assert result.id == 100
    payment_repo.get_by_id.assert_awaited_once_with(100, CLINIC)


@pytest.mark.asyncio
async def test_service_get_payment_not_found(payment_repo, service):
    payment_repo.get_by_id.return_value = None

    with pytest.raises(PaymentNotFoundError):
        await service.get_payment(9999, CLINIC)


@pytest.mark.asyncio
async def test_service_list_delegates_to_repo(payment_repo, service):
    items = [_payment(), _payment(overrides={"id": 101})]
    payment_repo.list.return_value = (items, 2)

    d_from = datetime(2026, 1, 1, tzinfo=UTC)
    d_to = datetime(2026, 2, 1, tzinfo=UTC)

    result_items, total = await service.list_payments(
        CLINIC,
        appointment_id=None,
        from_date=d_from,
        to_date=d_to,
        status=PaymentStatus.PAID,
        page=2,
        page_size=1,
    )

    assert total == 2
    assert len(result_items) == 2
    payment_repo.list.assert_awaited_once_with(
        clinic_id=CLINIC,
        appointment_id=None,
        from_date=d_from,
        to_date=d_to,
        status=PaymentStatus.PAID,
        page=2,
        page_size=1,
    )
