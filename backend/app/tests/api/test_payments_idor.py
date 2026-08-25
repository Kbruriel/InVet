"""Tests de IDOR/BOLA para pagos operativos (BE-011-T06).

Cubre AC-011-06/AC-011-07:
- 403 para propietario al crear/cancelar (rol sin permisos de escritura).
- 404 para clinico de otra clinicica al leer/cancelar (tenant isolation).
- 403 cuando el usuario no tiene clinica asociada.
- El listado usa exclusivamente el tenant del usuario autenticado.
"""

from __future__ import annotations

import pytest

import app.api.v1.routers.payments_router as payments_router_mod

PAYLOAD_OK = {
    "appointment_id": 1,
    "service_id": 1,
    "amount": 1000,
    "method": "cash",
    "amount_received": 1200,
}


def _as_user(payment_app: dict, role: str, clinic_id: int | None) -> None:
    async def user() -> dict:
        return {"user_id": 7, "clinic_id": clinic_id, "role": role}

    payment_app["app"].dependency_overrides[
        payments_router_mod.get_current_access_user
    ] = user


def _scoped_repo_get(payment_app: dict, payment, tenant_id: int) -> None:
    """Repo que solo expone el pago a su tenant (isolation simulada)."""

    async def get_by_id(payment_id: int, clinic_id: int):
        return payment if clinic_id == tenant_id else None

    payment_app["mock_payment_repo"].get_by_id = get_by_id


class TestPaymentsIDOR:
    """Permisos por rol y ownership por tenant en pagos."""

    @pytest.mark.asyncio
    async def test_owner_cannot_create_returns_403(self, payment_app: dict) -> None:
        _as_user(payment_app, "owner", 1)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 403
        payment_app["mock_payment_repo"].create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_owner_cannot_cancel_returns_403(self, payment_app: dict) -> None:
        _as_user(payment_app, "owner", 1)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/1/cancel")
        assert resp.status_code == 403
        payment_app["mock_payment_repo"].cancel.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_other_clinic_detail_returns_404(self, payment_app: dict) -> None:
        payment = payment_app["mock_payment_repo"].get_by_id.return_value
        _as_user(payment_app, "veterinarian", 99)
        _scoped_repo_get(payment_app, payment, tenant_id=1)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments/1")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_other_clinic_cancel_returns_404(self, payment_app: dict) -> None:
        payment = payment_app["mock_payment_repo"].get_by_id.return_value
        _as_user(payment_app, "veterinarian", 99)
        _scoped_repo_get(payment_app, payment, tenant_id=1)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments/1/cancel")
        assert resp.status_code == 404
        payment_app["mock_payment_repo"].cancel.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_user_without_clinic_detail_returns_403(self, payment_app: dict) -> None:
        _as_user(payment_app, "staff", None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments/1")
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_user_without_clinic_create_returns_403(self, payment_app: dict) -> None:
        _as_user(payment_app, "staff", None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 403
        payment_app["mock_payment_repo"].create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_list_scoped_to_authenticated_clinic(self, payment_app: dict) -> None:
        from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
        from datetime import UTC, datetime

        def _pay(clinic: int) -> Payment:
            return Payment(
                id=1,
                appointment_id=1,
                service_id=1,
                clinic_id=clinic,
                amount=1000,
                method=PaymentMethod.CASH,
                amount_received=1200,
                change_amount=200,
                status=PaymentStatus.PAID,
                paid_at=datetime.now(UTC),
            )

        async def list_scoped(
            clinic_id, appointment_id=None, from_date=None, to_date=None, status=None, page=1, page_size=20
        ):
            items = [_pay(clinic_id)] if clinic_id == 99 else []
            return items, len(items)

        payment_app["mock_payment_repo"].list = list_scoped
        _as_user(payment_app, "staff", 99)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments")
        assert resp.status_code == 200
        body = resp.json()
        assert body["meta"]["total"] == 1
        assert body["items"][0]["clinic_id"] == 99
