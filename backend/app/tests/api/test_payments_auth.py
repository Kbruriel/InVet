"""Tests de autenticacion para pagos operativos (BE-011-T06).

Cubre AC-011-07: 401 cuando no hay token en los cuatro endpoints de pagos.
"""

from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.payments_router as payments_router_mod

PAYLOAD_OK = {
    "appointment_id": 1,
    "service_id": 1,
    "amount": 1000,
    "method": "cash",
    "amount_received": 1200,
}


def _unauthenticated_app() -> FastAPI:
    """App con router de pagos pero SIN override de autenticacion."""

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
    return app


class TestPaymentsAuth:
    """401 sin token en cada endpoint de pagos."""

    @pytest.mark.asyncio
    async def test_create_without_token_returns_401(self) -> None:
        app = _unauthenticated_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as client:
            resp = await client.post("/api/v1/payments", json=PAYLOAD_OK)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_detail_without_token_returns_401(self) -> None:
        app = _unauthenticated_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as client:
            resp = await client.get("/api/v1/payments/1")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_without_token_returns_401(self) -> None:
        app = _unauthenticated_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as client:
            resp = await client.get("/api/v1/payments")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_cancel_without_token_returns_401(self) -> None:
        app = _unauthenticated_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as client:
            resp = await client.post("/api/v1/payments/1/cancel")
        assert resp.status_code == 401
