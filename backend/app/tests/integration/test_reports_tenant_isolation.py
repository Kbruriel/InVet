"""Tests de seguridad: aislamiento multi-tenant de reportes (BE-015-T09, AC-015-11).

Verifica que el alcance de cada request se acota EXCLUSIVAMENTE a la clinica
del token JWT (Clinica A no puede exponer datos de Clinica B) y que un
usuario sin clinica asociada recibe 403.

A diferencia de ``test_reports_auth.py`` (que audita solo el 401), aqui se
ejecuta la cadena completa autenticacion -> resolucion de clinica -> delegacion
al use-case, con tokens reales por clinica, y se afirma que el ``clinic_id``
recibido por el caso de uso es siempre el del token.

Validacion:
    python -m pytest backend/app/tests/integration/test_reports_tenant_isolation.py -q
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.reports_router as reports_mod
import app.core.security as security_mod
from app.api.v1.schemas.report_schemas import PaginatedResponse
from app.core.security import create_access_token

CLINIC_A = 111
CLINIC_B = 222


def _fake_db() -> Iterator[Any]:
    class _Fake:
        def close(self) -> None:
            pass

    yield _Fake()


@pytest.fixture
def tenant_app() -> Iterator[FastAPI]:
    app = FastAPI()
    app.include_router(reports_mod.router, prefix="/api/v1/reports")
    app.dependency_overrides[security_mod.get_db] = _fake_db
    app.dependency_overrides[reports_mod._db] = _fake_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client_factory(tenant_app: FastAPI):
    def _make() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=tenant_app),
            base_url="http://test",
        )

    return _make


def _clinic_token(clinic_id: int) -> str:
    return create_access_token(
        {"sub": "500", "clinic_id": clinic_id, "role": "veterinarian"}
    )


def _empty_pagination() -> PaginatedResponse[Any]:  # type: ignore[type-arg]
    return PaginatedResponse[Any](items=[], total=0, page=1, size=20)  # type: ignore[call-overload]


# --- Valid DTOs so each endpoint's ``response_model`` passes validation ---
from app.api.v1.schemas.report_schemas import (  # noqa: E402
    AppointmentSummaryDto,
    ConsultationSummaryDto,
    PaymentSummaryDto,
    PetCountDto,
    RatingSummaryDto,
    ServiceSummaryDto,
)


def _mock_for(uc_name: str) -> Any:
    """Devuelve el mock return_value correcto para cada use-case.

    /reports/pets retorna un PetCountDto PLANO (no paginado).
    """
    if uc_name == "uc_pets":
        return PetCountDto(clinic_id=CLINIC_A, active_count=3)

    items: list[Any]
    if uc_name == "uc_appointments":
        items = [
            AppointmentSummaryDto(
                id=1,
                clinic_id=CLINIC_A,
                appointment_type="consulta",
                status="completada",
                scheduled_start="2025-06-01T09:00:00+00:00",
                scheduled_end="2025-06-01T09:30:00+00:00",
            )
        ]
    elif uc_name == "uc_services":
        items = [
            ServiceSummaryDto(
                id=1,
                clinic_id=CLINIC_A,
                name="Consulta",
                price=100.0,
                duration_minutes=30,
                is_active=True,
            )
        ]
    elif uc_name == "uc_consultations":
        items = [
            ConsultationSummaryDto(
                id=1,
                clinic_id=CLINIC_A,
                diagnosis="Gastritis",
            )
        ]
    elif uc_name == "uc_ratings":
        items = [RatingSummaryDto(average_rating=4.5, total_reviews=10)]
    elif uc_name == "uc_payments":
        items = [
            PaymentSummaryDto(
                id=1,
                clinic_id=CLINIC_A,
                amount=100.0,
                payment_method="cash",
                status="paid",
                paid_at="2025-06-01T12:00:00+00:00",
            )
        ]
    else:
        items = []
    return PaginatedResponse[Any](  # type: ignore[call-overload]
        items=items, total=len(items), page=1, size=20
    )


class TestTenantA:
    @pytest.mark.asyncio
    async def test_clinic_a_scoped_to_own_clinic(self, client_factory) -> None:
        with patch.object(
            reports_mod, "uc_appointments", return_value=_empty_pagination()
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    headers={"Authorization": f"Bearer {_clinic_token(CLINIC_A)}"},
                )

        assert resp.status_code == 200, resp.text
        # El scope es SIEMPRE la clinica del token (no Clinica B).
        assert uc.call_args.kwargs["clinic_id"] == CLINIC_A
        assert uc.call_args.kwargs["clinic_id"] != CLINIC_B


class TestTenantB:
    @pytest.mark.asyncio
    async def test_clinic_b_scoped_to_own_clinic(self, client_factory) -> None:
        with patch.object(
            reports_mod, "uc_appointments", return_value=_empty_pagination()
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    headers={"Authorization": f"Bearer {_clinic_token(CLINIC_B)}"},
                )

        assert resp.status_code == 200, resp.text
        assert uc.call_args.kwargs["clinic_id"] == CLINIC_B
        assert uc.call_args.kwargs["clinic_id"] != CLINIC_A


class TestNoAmplificationOnOtherEndpoints:
    """El clinic_id se acota igual en los demas endpoints (misma regla por defecto)."""

    @pytest.mark.parametrize(
        ("endpoint", "uc_name"),
        [
            ("/api/v1/reports/services", "uc_services"),
            ("/api/v1/reports/consultations", "uc_consultations"),
            ("/api/v1/reports/pets", "uc_pets"),
            ("/api/v1/reports/ratings", "uc_ratings"),
            ("/api/v1/reports/payments", "uc_payments"),
        ],
    )
    @pytest.mark.asyncio
    async def test_each_endpoint_scoped_to_token_clinic(
        self, client_factory, endpoint, uc_name
    ) -> None:
        with patch.object(
            reports_mod, uc_name, return_value=_mock_for(uc_name)
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    endpoint,
                    headers={"Authorization": f"Bearer {_clinic_token(CLINIC_A)}"},
                )

        assert resp.status_code == 200, resp.text
        assert uc.call_args.kwargs["clinic_id"] == CLINIC_A
        assert uc.call_args.kwargs["clinic_id"] != CLINIC_B


class TestUserWithoutClinic:
    @pytest.mark.asyncio
    async def test_token_without_clinic_403(self, client_factory) -> None:
        # Token válido de acceso pero SIN clinica resuelta -> 403 (no 401).
        from app.api.v1.schemas.report_schemas import PaginatedResponse

        token = create_access_token({"sub": "501", "role": "owner"})  # sin clinic_id

        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse[Any](items=[], total=0, page=1, size=20),  # type: ignore[call-overload]
        ) as uc:
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    headers={"Authorization": f"Bearer {token}"},
                )

        assert resp.status_code == 403, resp.text
        uc.assert_not_called()
