"""Tests de API para crear pagos operativos (BE-011-T05).

Cubre los casos C1–C6 de APIA-011:
- C1: POST /payments valida cuerpo (201 / 422).
- C2: Cita inexistente o de otra clinica -> 404.
- C3: Servicio inexistente, inactivo o de otra clinica -> 422.
- C4: Metodo CASH con recibido < cargo -> 422; cambio devuelto en respuesta.
- C5: 401 cuando no hay token; 403 para roles no clinicos (propietario/owner).
- C6: ``created_by`` se resuelve del usuario autenticado (tenant isolation).
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import app.api.v1.routers.payments_router as payments_router_mod

PAYLOAD_OK = {
    "appointment_id": 1,
    "service_id": 1,
    "amount": 1000,
    "method": "cash",
    "amount_received": 1200,
}


class TestCreatePaymentAPI:
    """Casos C1–C6 para POST /api/v1/payments."""

    @pytest.mark.asyncio
    async def test_c1_success_returns_201_with_change_amount(
        self, payment_app: dict
    ) -> None:
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["id"] == 1
        assert body["amount"] == 1000
        assert body["amount_received"] == 1200
        assert body["change_amount"] == 200
        assert body["status"] == "paid"
        assert "paid_at" in body

    @pytest.mark.asyncio
    async def test_c1_success_non_cash_no_change_amount(self, payment_app: dict) -> None:
        from datetime import UTC, datetime

        from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus

        # El use case no calcula cambio para metodos no CASH.
        created = Payment(
            id=1,
            appointment_id=1,
            service_id=1,
            clinic_id=1,
            amount=1000,
            method=PaymentMethod.CARD,
            amount_received=None,
            change_amount=None,
            status=PaymentStatus.PAID,
            paid_at=datetime.now(UTC),
        )
        payment_app["mock_payment_repo"].create = AsyncMock(return_value=created)

        client = payment_app["client_factory"]()
        payload = {**PAYLOAD_OK, "method": "card", "amount_received": None}
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 201, resp.text
        assert resp.json()["change_amount"] is None

    @pytest.mark.asyncio
    async def test_c1_invalid_body_returns_422(self, payment_app: dict) -> None:
        client = payment_app["client_factory"]()
        payload = {
            "appointment_id": 1,
            "service_id": 1,
            "amount": "no-entier",  # type: ignore[typeddict-item]
            "method": "cash",
            "amount_received": 1200,
        }
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422
        assert "detail" in resp.json()

    @pytest.mark.asyncio
    async def test_c2_missing_appointment_returns_404(self, payment_app: dict) -> None:
        payment_app["mock_appointment_repo"].get_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 404, resp.text

    @pytest.mark.asyncio
    async def test_c3_missing_service_returns_422(self, payment_app: dict) -> None:
        payment_app["mock_service_repo"].get_service_by_id = AsyncMock(return_value=None)
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 422, resp.text

    @pytest.mark.asyncio
    async def test_c3_inactive_service_returns_422(self, payment_app: dict) -> None:
        from app.domain.entities.service import Service
        from datetime import UTC, datetime

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

    @pytest.mark.asyncio
    async def test_c4_cash_received_less_than_amount_returns_422(
        self, payment_app: dict
    ) -> None:
        payload = {**PAYLOAD_OK, "amount_received": 500}
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_c4_cash_missing_received_returns_422(self, payment_app: dict) -> None:
        payload = {**PAYLOAD_OK, "amount_received": None}
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=payload)
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_c5_unauthenticated_returns_401(self) -> None:
        # Sin override de get_current_access_user: oauth2_scheme exige token
        # y responde 401 si falta cabecera Authorization.
        import httpx
        from fastapi import FastAPI

        class _Q:
            def filter(self, *a, **k):
                return self

            def first(self):
                return None

        class _S:
            def close(self):
                pass

            def query(self, *a, **k):
                return _Q()

        app = FastAPI()
        app.include_router(payments_router_mod.router, prefix="/api/v1")

        async def fake_db():
            yield _S()

        app.dependency_overrides[payments_router_mod.get_current_db] = fake_db
        app.dependency_overrides[payments_router_mod.get_payment_repo] = lambda: object()
        app.dependency_overrides[payments_router_mod.get_appointment_repo] = lambda: object()
        app.dependency_overrides[payments_router_mod.get_service_repo] = lambda: object()
        app.dependency_overrides[payments_router_mod.get_internal_user_repo] = lambda: object()

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_c5_owner_role_returns_403(self, payment_app: dict) -> None:
        async def owner_user() -> dict:
            return {"user_id": 1, "clinic_id": 1, "role": "owner"}

        payment_app["app"].dependency_overrides[
            payments_router_mod.get_current_access_user
        ] = owner_user

        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_c6_created_by_resolved_from_internal_user(
        self, payment_app: dict
    ) -> None:
        internal_user = AsyncMock()
        internal_user.id = 42
        payment_app["mock_internal_user_repo"].get_by_user_id = AsyncMock(
            return_value=internal_user
        )

        created_payment = payment_app["mock_payment_repo"].create
        client = payment_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 201
        created_payment.assert_awaited_once()
        domain_payment = created_payment.await_args.args[0]
        assert domain_payment.created_by == 42
