"""Tests de API para leer pagos operativos (BE-011-T05).

Cubre:
- C7: GET /payments/{id} 200 con pago del tenant; 404 si no existe o es de
  otra clinica (tenant isolation)
- C9: GET /payments paginado con ``{items, meta}`` y filtros opcionales
  (appointment_id, fecha_from/fecha_to, estado)
- C12: 403 cuando el usuario no tiene clinica asociada
"""

from __future__ import annotations

from datetime import UTC, datetime

from unittest.mock import AsyncMock

import pytest

import app.api.v1.routers.payments_router as payments_router_mod


class TestGetPaymentAPI:
    @pytest.mark.asyncio
    async def test_c7_get_existing_returns_200(self, payment_app: dict) -> None:
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments/1")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["id"] == 1
        assert body["status"] == "paid"

    @pytest.mark.asyncio
    async def test_c7_get_missing_returns_404(self, payment_app: dict) -> None:
        payment_app["mock_payment_repo"].get_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments/999")
        assert resp.status_code == 404, resp.text

    @pytest.mark.asyncio
    async def test_c7_tenant_isolation_queries_with_user_clinic(
        self, payment_app: dict
    ) -> None:
        async def other_clinic_user() -> dict:
            return {"user_id": 1, "clinic_id": 999, "role": "staff"}

        payment_app["app"].dependency_overrides[
            payments_router_mod.get_current_access_user
        ] = other_clinic_user

        # El repos solo conoc el pago clinic_id=1 (tenant isolation).
        async def fake_get(payment_id, clinic_id):
            return None if clinic_id != 1 else _default_payment_stub()

        payment_app["mock_payment_repo"].get_by_id = AsyncMock(
            side_effect=fake_get
        )

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments/1")
        assert resp.status_code == 404
        args, _ = payment_app["mock_payment_repo"].get_by_id.await_args
        assert args[1] == 999


def _default_payment_stub():
    from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus

    return Payment(
        id=1,
        appointment_id=1,
        service_id=1,
        clinic_id=1,
        amount=1000,
        method=PaymentMethod.CASH,
        amount_received=1200,
        change_amount=200,
        status=PaymentStatus.PAID,
        paid_at=datetime.now(UTC),
    )


class TestListPaymentsAPI:
    @pytest.mark.asyncio
    async def test_c9_list_returns_items_and_meta(self, payment_app: dict) -> None:
        payment_app["mock_payment_repo"].list = AsyncMock(
            return_value=([_default_payment_stub(), _default_payment_stub()], 2)
        )
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments", params={"page": 1, "page_size": 10})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert isinstance(body["items"], list)
        assert len(body["items"]) == 2
        assert body["meta"]["page"] == 1
        assert body["meta"]["page_size"] == 10
        assert body["meta"]["total"] == 2
        assert body["meta"]["pages"] == 1

    @pytest.mark.asyncio
    async def test_c9_list_applies_filters(self, payment_app: dict) -> None:
        list_mock = AsyncMock(return_value=([], 0))
        payment_app["mock_payment_repo"].list = list_mock

        frm = "2026-01-01T00:00:00Z"
        to = "2026-12-31T23:59:59Z"
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get(
                "/api/v1/payments",
                params={
                    "page": 2,
                    "page_size": 5,
                    "appointment_id": 42,
                    "from_date": frm,
                    "to_date": to,
                    "status": "paid",
                },
            )
        assert resp.status_code == 200

        args, kwargs = list_mock.await_args
        assert kwargs["clinic_id"] == 1
        assert kwargs["appointment_id"] == 42
        assert kwargs["from_date"] is not None
        assert kwargs["to_date"] is not None
        assert kwargs["status"].value == "paid"
        assert kwargs["page"] == 2
        assert kwargs["page_size"] == 5

    @pytest.mark.asyncio
    async def test_c9_list_invalid_page_returns_422(self, payment_app: dict) -> None:
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments", params={"page": 0})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_c12_user_without_clinic_returns_403(self, payment_app: dict) -> None:
        async def no_clinic_user() -> dict:
            return {"user_id": 1, "role": "staff"}

        payment_app["app"].dependency_overrides[
            payments_router_mod.get_current_access_user
        ] = no_clinic_user

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/payments/1")
        assert resp.status_code == 403
