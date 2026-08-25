"""Fixture compartida para tests de API de pagos operativos (BE-011-T05).

Crea una aplicacion FastAPI con el router de pagos y las dependencias de
repositorio sobrescritas con ``AsyncMock``. Permite sobreescribir el
usuario autenticado (``get_current_access_user``) por prueba.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from unittest.mock import AsyncMock

import app.api.v1.routers.payments_router as payments_router_mod
from app.api.v1.routers.payments_router import router
from app.domain.entities.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.domain.entities.service import Service


def _default_appointment() -> Appointment:
    return Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(UTC),
        scheduled_end=datetime.now(UTC) + timedelta(minutes=30),
        status=AppointmentStatus.PENDING,
    )


def _default_service() -> Service:
    now = datetime.now(UTC)
    return Service(
        id=1,
        clinic_id=1,
        name="Consulta",
        description="",
        price=50.0,
        duration_minutes=30,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def _default_payment() -> Payment:
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


@pytest.fixture
def payment_app() -> Iterator[dict[str, Any]]:
    """App FastAPI con mock repos y usuario por defecto role=staff/clinic_id=1."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    async def mocked_user() -> dict[str, Any]:
        return {"user_id": 1, "clinic_id": 1, "role": "staff"}

    def fake_db() -> Iterator[Any]:
        class FakeSession:
            def close(self) -> None:
                pass

        yield FakeSession()

    app.dependency_overrides[payments_router_mod.get_current_db] = fake_db
    app.dependency_overrides[payments_router_mod.get_current_access_user] = mocked_user

    mock_payment_repo = AsyncMock()
    mock_payment_repo.get_by_id = AsyncMock(return_value=_default_payment())
    mock_payment_repo.create = AsyncMock(return_value=_default_payment())
    mock_payment_repo.cancel = AsyncMock(return_value=_default_payment())
    mock_payment_repo.list = AsyncMock(return_value=([_default_payment()], 1))

    mock_appointment_repo = AsyncMock()
    mock_appointment_repo.get_by_id = AsyncMock(return_value=_default_appointment())

    mock_service_repo = AsyncMock()
    mock_service_repo.get_service_by_id = AsyncMock(return_value=_default_service())

    mock_internal_user_repo = AsyncMock()
    mock_internal_user_repo.get_by_user_id = AsyncMock(return_value=None)

    app.dependency_overrides[payments_router_mod.get_payment_repo] = lambda: mock_payment_repo
    app.dependency_overrides[payments_router_mod.get_appointment_repo] = lambda: mock_appointment_repo
    app.dependency_overrides[payments_router_mod.get_service_repo] = lambda: mock_service_repo
    app.dependency_overrides[payments_router_mod.get_internal_user_repo] = lambda: mock_internal_user_repo

    yield {
        "app": app,
        "client_factory": lambda: httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ),
        "mock_payment_repo": mock_payment_repo,
        "mock_appointment_repo": mock_appointment_repo,
        "mock_service_repo": mock_service_repo,
        "mock_internal_user_repo": mock_internal_user_repo,
    }

    app.dependency_overrides.clear()
