"""Tests de contrato: entradas invalidas en reportes (BE-015-T10, AC-015-10).

Austar que cada endpoint RECHAZA con 422 (Unprocessable Entity) los inputs
invalidos y NUNCA delega al caso de uso:

- ``period_start`` / ``period_end`` con formato distinto a ``YYYY-MM-DD``
- ``period_end`` anterior a ``period_start``
- paginacion fuera de rango: ``page < 1``, ``size < 1``, ``size > 100``
- parametros no enteros (coercion de query)

Validacion:
    python -m pytest backend/app/tests/integration/test_reports_invalid_input.py -q
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.reports_router as reports_mod
from app.api.v1.schemas.report_schemas import PaginatedResponse

CLINIC_ID = 777


def _fake_user() -> dict[str, Any]:
    return {"user_id": 3, "clinic_id": CLINIC_ID, "role": "veterinarian"}


def _fake_db() -> Iterator[Any]:
    class _Fake:
        def close(self) -> None:
            pass

    yield _Fake()


@pytest.fixture
def reports_app() -> Iterator[FastAPI]:
    app = FastAPI()
    app.include_router(reports_mod.router, prefix="/api/v1/reports")
    app.dependency_overrides[reports_mod.get_current_access_user] = _fake_user
    app.dependency_overrides[reports_mod._db] = _fake_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client_factory(reports_app: FastAPI):
    def _make() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=reports_app),
            base_url="http://test",
        )

    return _make


ALL_ENDPOINTS = [
    "/api/v1/reports/appointments",
    "/api/v1/reports/services",
    "/api/v1/reports/pets",
    "/api/v1/reports/consultations",
    "/api/v1/reports/ratings",
    "/api/v1/reports/payments",
]

PAGED_ENDPOINTS = [
    "/api/v1/reports/appointments",
    "/api/v1/reports/services",
    "/api/v1/reports/consultations",
    "/api/v1/reports/payments",
]

# Mapeo endpoint -> atributo de use-case en el router (para bloquear su ejecucion).
_UC_FOR = {
    "/api/v1/reports/appointments": "uc_appointments",
    "/api/v1/reports/services": "uc_services",
    "/api/v1/reports/pets": "uc_pets",
    "/api/v1/reports/consultations": "uc_consultations",
    "/api/v1/reports/ratings": "uc_ratings",
    "/api/v1/reports/payments": "uc_payments",
}


class TestPeriodDateValidation:
    @pytest.mark.parametrize("endpoint", ALL_ENDPOINTS)
    @pytest.mark.asyncio
    async def test_invalid_period_start_format_422(
        self, client_factory, endpoint
    ) -> None:
        with patch.object(reports_mod, _UC_FOR[endpoint]) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(endpoint, params={"period_start": "01/06/2025"})

        assert resp.status_code == 422, (endpoint, resp.text)
        assert "YYYY-MM-DD" in resp.json()["detail"]
        uc.assert_not_called()

    @pytest.mark.parametrize("endpoint", ALL_ENDPOINTS)
    @pytest.mark.asyncio
    async def test_invalid_period_end_format_422(
        self, client_factory, endpoint
    ) -> None:
        with patch.object(reports_mod, _UC_FOR[endpoint]) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(endpoint, params={"period_end": "25-12-20"})

        assert resp.status_code == 422, (endpoint, resp.text)
        assert "YYYY-MM-DD" in resp.json()["detail"]
        uc.assert_not_called()

    @pytest.mark.parametrize("endpoint", ALL_ENDPOINTS)
    @pytest.mark.asyncio
    async def test_end_before_start_422(self, client_factory, endpoint) -> None:
        with patch.object(reports_mod, _UC_FOR[endpoint]) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    endpoint,
                    params={"period_start": "2025-06-30", "period_end": "2025-06-01"},
                )

        assert resp.status_code == 422, (endpoint, resp.text)
        assert "anterior" in resp.json()["detail"]
        uc.assert_not_called()


class TestPaginationValidation:
    @pytest.mark.parametrize("endpoint", PAGED_ENDPOINTS)
    @pytest.mark.asyncio
    async def test_page_below_minimum_422(self, client_factory, endpoint) -> None:
        with patch.object(reports_mod, _UC_FOR[endpoint]) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(endpoint, params={"page": 0})

        assert resp.status_code == 422, (endpoint, resp.text)
        uc.assert_not_called()

    @pytest.mark.parametrize("endpoint", PAGED_ENDPOINTS)
    @pytest.mark.asyncio
    async def test_size_above_maximum_422(self, client_factory, endpoint) -> None:
        with patch.object(reports_mod, _UC_FOR[endpoint]) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(endpoint, params={"size": 1000})

        assert resp.status_code == 422, (endpoint, resp.text)
        uc.assert_not_called()

    @pytest.mark.parametrize("endpoint", PAGED_ENDPOINTS)
    @pytest.mark.asyncio
    async def test_non_integer_page_422(self, client_factory, endpoint) -> None:
        with patch.object(reports_mod, _UC_FOR[endpoint]) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(endpoint, params={"page": "uno"})

        # ``page`` es ``Query(int)``: un valor no entero genera 422 del framework.
        assert resp.status_code == 422, (endpoint, resp.text)
        uc.assert_not_called()


class TestPageSizeRespected:
    @pytest.mark.asyncio
    async def test_valid_page_size_forwarded(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse(items=[], total=42, page=3, size=5),
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments", params={"page": 3, "size": 5}
                )

        assert resp.status_code == 200, resp.text
        assert resp.json()["page"] == 3
        assert resp.json()["size"] == 5
        assert uc.call_args.kwargs["page"] == 3
        assert uc.call_args.kwargs["size"] == 5
