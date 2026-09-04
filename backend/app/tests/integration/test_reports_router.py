"""Tests de integracion: router HTTP de reportes (BE-015-T08).

Sube el ``reports_router`` en una FastAPI real, sobreescribe la autenticacion
(``get_current_access_user``) y la sesion de datos (``_db``), y patchea los
seis casos de uso (atributos de modulo ``uc_*``) para verificar que cada
endpoint:

- responde 200 con el contrato JSON esperado (estructura + types)
- aplica tenant isolation (403 si el token no tiene ``clinic_id``)
- valida fechas (422 para formato invalido / period_end < period_start)

Los casos de uso se ejecutan contra la capa de datos en unit tests
(``app/tests/usecases/*``); aqui se aseguran el wiring del router, el
prefijo ``/api/v1/reports`` y la resolucion de dependencias.

Validacion:
    python -m pytest backend/app/tests/integration/test_reports_router.py -q
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.reports_router as reports_mod
from app.api.v1.schemas.report_schemas import (
    AppointmentSummaryDto,
    ConsultationSummaryDto,
    PaginatedResponse,
    PaymentSummaryDto,
    PetCountDto,
    RatingSummaryDto,
    ServiceSummaryDto,
)

CLINIC_ID = 42


def _fake_user() -> dict[str, Any]:
    return {"user_id": 7, "clinic_id": CLINIC_ID, "role": "veterinarian"}


def _user_without_clinic() -> dict[str, Any]:
    return {"user_id": 7, "role": "owner"}


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


def _dto_appointments() -> list[AppointmentSummaryDto]:
    return [
        AppointmentSummaryDto(
            id=1,
            clinic_id=CLINIC_ID,
            pet_name="Firulais",
            owner_name="Luna",
            veterinarian_name="Dra. Gomez",
            appointment_type="consulta",
            status="completada",
            scheduled_start="2025-06-01T09:00:00+00:00",
            scheduled_end="2025-06-01T09:30:00+00:00",
        )
    ]


def _dto_services() -> list[ServiceSummaryDto]:
    return [
        ServiceSummaryDto(
            id=1,
            clinic_id=CLINIC_ID,
            name="Consulta general",
            description="Evaluacion",
            price=150.0,
            duration_minutes=30,
            is_active=True,
        )
    ]


def _dto_consultations() -> list[ConsultationSummaryDto]:
    return [
        ConsultationSummaryDto(
            id=1,
            clinic_id=CLINIC_ID,
            pet_name="Firulais",
            veterinarian_name="Dra. Gomez",
            diagnosis="Gastritis",
            history="Malestar",
            recommendations="Dienetica",
        )
    ]


def _dto_ratings() -> list[RatingSummaryDto]:
    return [
        RatingSummaryDto(veterinarian_id=None, average_rating=4.5, total_reviews=80)
    ]


def _dto_payments() -> list[PaymentSummaryDto]:
    return [
        PaymentSummaryDto(
            id=1,
            clinic_id=CLINIC_ID,
            appointment_id=10,
            service_id=100,
            amount=250.0,
            payment_method="card",
            status="paid",
            paid_at="2025-06-01T12:00:00+00:00",
        )
    ]


class TestReportsRouterPaginationEndpoints:
    @pytest.mark.asyncio
    async def test_appointments_200_contract(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse(
                items=_dto_appointments(), total=1, page=1, size=20
            ),
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/appointments")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert body["size"] == 20
        assert body["items"][0]["pet_name"] == "Firulais"
        assert body["items"][0]["veterinarian_name"] == "Dra. Gomez"
        # El router deriva clinic_id del token JWT (tenant isolation)
        assert uc.call_args.kwargs["clinic_id"] == CLINIC_ID

    @pytest.mark.asyncio
    async def test_services_200_contract(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_services",
            return_value=PaginatedResponse(
                items=_dto_services(), total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/services")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["name"] == "Consulta general"
        assert body["items"][0]["price"] == 150.0

    @pytest.mark.asyncio
    async def test_consultations_200_contract(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_consultations",
            return_value=PaginatedResponse(
                items=_dto_consultations(), total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/consultations")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["diagnosis"] == "Gastritis"
        assert body["items"][0]["recommendations"] == "Dienetica"

    @pytest.mark.asyncio
    async def test_payments_200_contract_with_total_amount(
        self, client_factory
    ) -> None:
        with patch.object(
            reports_mod,
            "uc_payments",
            return_value=PaginatedResponse(
                items=_dto_payments(), total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/payments")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 1
        assert body["items"][0]["amount"] == 250.0
        assert body["total_amount"] == 250.0

    @pytest.mark.asyncio
    async def test_pets_200_contract(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_pets",
            return_value=PaginatedResponse(
                items=[PetCountDto(clinic_id=CLINIC_ID, active_count=12)],
                total=1,
                page=1,
                size=1,
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/pets")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["clinic_id"] == CLINIC_ID
        assert body["active_count"] == 12

    @pytest.mark.asyncio
    async def test_ratings_200_contract_with_clinic_avg(self, client_factory) -> None:
        two = [
            RatingSummaryDto(veterinarian_id=None, average_rating=4.0, total_reviews=10),
            RatingSummaryDto(veterinarian_id=None, average_rating=5.0, total_reviews=5),
        ]
        with patch.object(
            reports_mod,
            "uc_ratings",
            return_value=PaginatedResponse(items=two, total=2, page=1, size=20),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/ratings")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert len(body["by_veterinarian"]) == 2
        # clinic_avg = (4.0 + 5.0) / 2 = 4.5
        assert body["clinic_avg"] == 4.5


class TestReportsRouterPaginationParams:
    @pytest.mark.asyncio
    async def test_page_size_forwarded(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse(items=[], total=10, page=2, size=5),
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    params={"page": 2, "size": 5},
                )

        assert resp.status_code == 200, resp.text
        assert resp.json()["page"] == 2
        assert resp.json()["size"] == 5
        assert uc.call_args.kwargs["page"] == 2
        assert uc.call_args.kwargs["size"] == 5

    @pytest.mark.asyncio
    async def test_size_upper_bound_422(self, client_factory) -> None:
        with patch.object(reports_mod, "uc_appointments"):
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    params={"size": 1000},
                )

        assert resp.status_code == 422


class TestReportsRouterTenantIsolation:
    @pytest.mark.asyncio
    async def test_403_when_token_lacks_clinic(
        self, reports_app, client_factory
    ) -> None:
        # El fixture ``reports_app`` ya registro ``get_current_access_user``;
        # lo sobreescribimos por una identidad sin clinica.
        reports_app.dependency_overrides[reports_mod.get_current_access_user] = (
            _user_without_clinic
        )
        with patch.object(
            reports_mod,
            "uc_appointments",
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/appointments")

        assert resp.status_code == 403, resp.text
        uc.assert_not_called()


class TestReportsRouterDateValidation:
    @pytest.mark.asyncio
    async def test_bad_date_format_422(self, client_factory) -> None:
        with patch.object(reports_mod, "uc_appointments") as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    params={"period_start": "01-01-2025"},
                )

        assert resp.status_code == 422, resp.text
        uc.assert_not_called()

    @pytest.mark.asyncio
    async def test_end_before_start_422(self, client_factory) -> None:
        with patch.object(reports_mod, "uc_appointments") as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    params={
                        "period_start": "2025-06-30",
                        "period_end": "2025-06-01",
                    },
                )

        assert resp.status_code == 422, resp.text
        uc.assert_not_called()

    @pytest.mark.asyncio
    async def test_valid_period_passed_through(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse(items=[], total=0, page=1, size=20),
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    params={"period_start": "2025-06-01", "period_end": "2025-06-30"},
                )

        assert resp.status_code == 200, resp.text
        kwargs = uc.call_args.kwargs
        assert kwargs["period_start"].strftime("%Y-%m-%d") == "2025-06-01"
        assert kwargs["period_end"].strftime("%Y-%m-%d") == "2025-06-30"
