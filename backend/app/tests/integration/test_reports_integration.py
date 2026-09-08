"""Tests E2E de contrato API de reportes (BE-015-T10, AC-015-03 / AC-015-04).

Levanta el ``reports_router`` sobre una FastAPI real (wiring real: prefijo
``/api/v1/reports``, resolucion de dependencias, ``response_model``), provee
una autenticacion fija sobreescribiendo ``get_current_access_user`` y una
sesion inerte, y valida el CONTRATO COMPLETO de cada endpoint: forma de
respuesta (paginada / flat / ratings / payments) + tipos campo por campo.

Los casos de uso se mockean para inyectar datos conocidos; el objetivo es
austar que el JSON devuelto cumple el esquema de cada DTO.

Validacion:
    python -m pytest backend/app/tests/integration/test_reports_integration.py -q
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

CLINIC_ID = 900


def _fake_user() -> dict[str, Any]:
    return {"user_id": 42, "clinic_id": CLINIC_ID, "role": "veterinarian"}


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


# --- Datos de fixture con las 9 claves de cada DTO ---


def _appointment() -> AppointmentSummaryDto:
    return AppointmentSummaryDto(
        id=1,
        clinic_id=CLINIC_ID,
        pet_name="Max",
        owner_name="Ana",
        veterinarian_name="Dra. Lopez",
        appointment_type="urgencia",
        status="completada",
        scheduled_start="2025-06-01T09:00:00+00:00",
        scheduled_end="2025-06-01T09:30:00+00:00",
    )


def _service() -> ServiceSummaryDto:
    return ServiceSummaryDto(
        id=7,
        clinic_id=CLINIC_ID,
        name="Citas de Control",
        description="Evaluacion general",
        price=150.5,
        duration_minutes=45,
        is_active=True,
    )


def _consultation() -> ConsultationSummaryDto:
    return ConsultationSummaryDto(
        id=3,
        clinic_id=CLINIC_ID,
        pet_name="Max",
        veterinarian_name="Dra. Lopez",
        diagnosis="Gastroenteritis",
        history="Vomitos 2 dias",
        recommendations="Dienetica blanda",
    )


def _rating(vet_id: int | None, avg: float, reviews: int) -> RatingSummaryDto:
    return RatingSummaryDto(
        veterinarian_id=vet_id, average_rating=avg, total_reviews=reviews
    )


def _payment(amount: float, method: str) -> PaymentSummaryDto:
    return PaymentSummaryDto(
        id=11,
        clinic_id=CLINIC_ID,
        appointment_id=21,
        service_id=31,
        amount=amount,
        payment_method=method,
        status="paid",
        paid_at="2025-06-01T14:00:00+00:00",
    )


class TestAppointmentsContract:
    @pytest.mark.asyncio
    async def test_schema_validates_against_dto(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse(
                items=[_appointment()], total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/appointments")

        assert resp.status_code == 200, resp.text
        body = resp.json()

        # Forma paginada
        assert isinstance(body, dict)
        assert set(body.keys()) == {"items", "total", "page", "size"}
        assert body["total"] == 1
        assert body["page"] == 1
        assert body["size"] == 20

        item = body["items"][0]
        assert set(item.keys()) == {
            "id",
            "clinic_id",
            "pet_name",
            "owner_name",
            "veterinarian_name",
            "appointment_type",
            "status",
            "scheduled_start",
            "scheduled_end",
        }
        assert isinstance(item["id"], int)
        assert isinstance(item["clinic_id"], int)
        assert isinstance(item["appointment_type"], str)
        assert isinstance(item["status"], str)
        assert isinstance(item["scheduled_start"], str)
        assert isinstance(item["scheduled_end"], str)
        # El DTO se revalida limpiamente contra el esquema (AC-015-03)
        AppointmentSummaryDto.model_validate(item)


class TestServicesContract:
    @pytest.mark.asyncio
    async def test_schema_validates_against_dto(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_services",
            return_value=PaginatedResponse(
                items=[_service()], total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/services")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) == {"items", "total", "page", "size"}

        item = body["items"][0]
        assert set(item.keys()) == {
            "id",
            "clinic_id",
            "name",
            "description",
            "price",
            "duration_minutes",
            "is_active",
        }
        assert isinstance(item["price"], float)
        assert isinstance(item["duration_minutes"], int)
        assert isinstance(item["is_active"], bool)
        ServiceSummaryDto.model_validate(item)


class TestPetsContract:
    @pytest.mark.asyncio
    async def test_returns_flat_pet_count(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_pets",
            return_value=PetCountDto(clinic_id=CLINIC_ID, active_count=25),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/pets")

        assert resp.status_code == 200, resp.text
        body = resp.json()

        # Forma PLATA (no paginada)
        assert set(body.keys()) == {"clinic_id", "active_count"}
        assert body["clinic_id"] == CLINIC_ID
        assert body["active_count"] == 25
        PetCountDto.model_validate(body)


class TestConsultationsContract:
    @pytest.mark.asyncio
    async def test_schema_validates_against_dto(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_consultations",
            return_value=PaginatedResponse(
                items=[_consultation()], total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/consultations")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) == {"items", "total", "page", "size"}

        item = body["items"][0]
        assert set(item.keys()) == {
            "id",
            "clinic_id",
            "pet_name",
            "veterinarian_name",
            "diagnosis",
            "history",
            "recommendations",
        }
        ConsultationSummaryDto.model_validate(item)


class TestRatingsContract:
    @pytest.mark.asyncio
    async def test_returns_by_veterinarian_and_clinic_avg(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_ratings",
            return_value=PaginatedResponse(
                items=[
                    _rating(None, 4.0, 10),
                    _rating(5, 5.0, 6),
                ],
                total=2,
                page=1,
                size=20,
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/ratings")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) == {"by_veterinarian", "clinic_avg"}

        assert isinstance(body["clinic_avg"], int | float)
        # Media ponderada (F2): sum(avg_v * total_reviews_v) / sum(total_reviews_v)
        # = (4.0 * 10 + 5.0 * 6) / (10 + 6) = 70 / 16 = 4.375 -> round(,2) = 4.38
        assert body["clinic_avg"] == 4.38

        assert isinstance(body["by_veterinarian"], list)
        assert len(body["by_veterinarian"]) == 2
        for row in body["by_veterinarian"]:
            assert set(row.keys()) == {
                "veterinarian_id",
                "average_rating",
                "total_reviews",
            }
            assert isinstance(row["total_reviews"], int)
            assert isinstance(row["average_rating"], int | float)


class TestPaymentsContract:
    @pytest.mark.asyncio
    async def test_returns_paged_with_total_amount(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_payments",
            return_value=PaginatedResponse(
                items=[_payment(100.5, "cash"), _payment(49.5, "card")],
                total=2,
                page=1,
                size=20,
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/payments")

        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert set(body.keys()) == {"items", "total", "page", "size", "total_amount"}
        assert body["total"] == 2
        assert body["total_amount"] == 150.0  # 100.5 + 49.5

        item = body["items"][0]
        assert set(item.keys()) == {
            "id",
            "clinic_id",
            "appointment_id",
            "service_id",
            "amount",
            "payment_method",
            "status",
            "paid_at",
        }
        PaymentSummaryDto.model_validate(item)

    @pytest.mark.asyncio
    async def test_total_amount_rounds_to_2(self, client_factory) -> None:
        with patch.object(
            reports_mod,
            "uc_payments",
            return_value=PaginatedResponse(
                items=[_payment(1.005, "cash")], total=1, page=1, size=20
            ),
        ):
            client = client_factory()
            async with client:
                resp = await client.get("/api/v1/reports/payments")

        assert resp.status_code == 200, resp.text
        assert resp.json()["total_amount"] == round(1.005, 2)
