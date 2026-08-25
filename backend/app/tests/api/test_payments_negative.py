"""Tests negativos para pagos operativos (QA-011-T02).

Cubre AC-011-02 y AC-011-05: rechazos de negocio con errores claros y sin
filtrado de stack traces ni detalles internos:
- cita inexistente o ajena al tenant -> 404
- servicio inexistente -> 422
- servicio inactivo -> 422
- metodo CASH con importe recibido menor al cargo (o ausente) -> 422
- monto no numerico / negativo -> 422 (validacion de esquema)
- cancelar un pago ya cancelado -> 409
- cancelar un pago inexistente -> 404

Los detalles HTTP deben coincidir con los mensajes publicos del dominio
(``PaymentError.message``): frases claras en espanol, sin traza interna.
"""

from __future__ import annotations

from datetime import UTC, datetime

from unittest.mock import AsyncMock

import pytest

from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.domain.entities.service import Service

PAYLOAD_OK = {
    "appointment_id": 1,
    "service_id": 1,
    "amount": 1000,
    "method": "cash",
    "amount_received": 1200,
}


class TestCreatePaymentNegative:
    """Rechazos de POST /api/v1/payments con mensajes claros."""

    @pytest.mark.asyncio
    async def test_missing_appointment_returns_404_clear_message(
        self, payment_app: dict
    ) -> None:
        payment_app["mock_appointment_repo"].get_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 404, resp.text
        assert resp.json()["detail"] == "La cita no existe o no es accesible."

    @pytest.mark.asyncio
    async def test_missing_service_returns_422_clear_message(
        self, payment_app: dict
    ) -> None:
        payment_app["mock_service_repo"].get_service_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 422, resp.text
        assert resp.json()["detail"] == "El servicio no existe o no es accesible."

    @pytest.mark.asyncio
    async def test_inactive_service_returns_422_clear_message(
        self, payment_app: dict
    ) -> None:
        now = datetime.now(UTC)
        payment_app["mock_service_repo"].get_service_by_id = AsyncMock(
            return_value=Service(
                id=1,
                clinic_id=1,
                name="Consulta",
                description="",
                price=50.0,
                duration_minutes=30,
                is_active=False,
                created_at=now,
                updated_at=now,
            )
        )
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 422
        assert resp.json()["detail"] == "Solo se puede registrar un pago con un servicio activo."

    @pytest.mark.asyncio
    async def test_cash_received_below_amount_returns_422_clear_message(
        self, payment_app: dict
    ) -> None:
        payload = {**PAYLOAD_OK, "amount_received": 500}
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422
        assert (
            resp.json()["detail"]
            == "El importe recibido debe ser mayor o igual al importe del pago."
        )

    @pytest.mark.asyncio
    async def test_cash_missing_received_returns_422(self, payment_app: dict) -> None:
        payload = {**PAYLOAD_OK, "amount_received": None}
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422
        assert "detail" in resp.json()

    @pytest.mark.asyncio
    async def test_non_numeric_amount_returns_422_validation_detail(
        self, payment_app: dict
    ) -> None:
        payload = {**PAYLOAD_OK, "amount": "no-entier"}  # type: ignore[typeddict-item]
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422
        assert isinstance(resp.json()["detail"], list)

    @pytest.mark.asyncio
    async def test_negative_amount_returns_422(self, payment_app: dict) -> None:
        payload = {**PAYLOAD_OK, "amount": -500}
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422
        # Validacion de esquema: cuerpo solo {detail: [...]}, sin internals.
        assert set(resp.json().keys()) == {"detail"}
        assert isinstance(resp.json()["detail"], list)


class TestCancelPaymentNegative:
    """Rechazos de POST /api/v1/payments/{id}/cancel."""

    def _payment(
        self, status: PaymentStatus, cancelled_at: datetime | None = None
    ) -> Payment:
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

    @pytest.mark.asyncio
    async def test_cancel_already_cancelled_returns_409_clear_message(
        self, payment_app: dict
    ) -> None:
        already = self._payment(PaymentStatus.CANCELLED, cancelled_at=datetime.now(UTC))
        payment_app["mock_payment_repo"].get_by_id = AsyncMock(return_value=already)
        cancel_mock = AsyncMock(return_value=already)
        payment_app["mock_payment_repo"].cancel = cancel_mock

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/7/cancel")
        assert resp.status_code == 409, resp.text
        assert resp.json()["detail"] == "El pago ya fue cancelado."
        cancel_mock.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_cancel_missing_returns_404_clear_message(
        self, payment_app: dict
    ) -> None:
        payment_app["mock_payment_repo"].get_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/7/cancel")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "El pago no existe o no es accesible."
