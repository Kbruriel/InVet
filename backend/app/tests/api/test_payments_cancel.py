"""Tests de API para cancelar pagos operativos (BE-011-T05).

Cubre:
- C10: POST /payments/{id}/cancel 200 con pago->CANCELLED y cancelled_at
- C11: Cancelar un pago ya CANCELLED -> 409
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus


def _payment(status: PaymentStatus, cancelled_at: datetime | None = None) -> Payment:
    return Payment(
        id=7,
        appointment_id=1,
        service_id=1,
        clinic_id=1,
        amount=1000,
        method=PaymentMethod.CARD,
        amount_received=None,
        change_amount=None,
        status=status,
        paid_at=datetime.now(UTC),
        cancelled_at=cancelled_at,
    )


class TestCancelPaymentAPI:
    @pytest.mark.asyncio
    async def test_c10_cancel_paid_returns_200_cancelled(
        self, payment_app: dict
    ) -> None:
        now = datetime.now(UTC)
        cancelled = _payment(PaymentStatus.CANCELLED, cancelled_at=now)
        payment_app["mock_payment_repo"].cancel = AsyncMock(return_value=cancelled)

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/7/cancel")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "cancelled"
        assert body["cancelled_at"] is not None

    @pytest.mark.asyncio
    async def test_c11_cancel_already_cancelled_returns_409(
        self, payment_app: dict
    ) -> None:
        # El repos devuelve un pago ya CANCELLED al consultarlo.
        already = _payment(PaymentStatus.CANCELLED, cancelled_at=datetime.now(UTC))
        payment_app["mock_payment_repo"].get_by_id = AsyncMock(return_value=already)
        cancel_mock = AsyncMock(return_value=already)
        payment_app["mock_payment_repo"].cancel = cancel_mock

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/7/cancel")
        assert resp.status_code == 409, resp.text
        cancel_mock.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_c10_cancel_missing_returns_404(self, payment_app: dict) -> None:
        payment_app["mock_payment_repo"].get_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/7/cancel")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_c10_cancel_by_owner_role_returns_403(
        self, payment_app: dict
    ) -> None:
        import app.api.v1.routers.payments_router as payments_router_mod

        async def owner_user() -> dict:
            return {"user_id": 1, "clinic_id": 1, "role": "owner"}

        payment_app["app"].dependency_overrides[
            payments_router_mod.get_current_access_user
        ] = owner_user

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/7/cancel")
        assert resp.status_code == 403
