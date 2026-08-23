"""Integration tests for prescription creation endpoint (BE-010, APIA-010 C1..C4)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import app.api.v1.routers.prescription_router as rx
from app.api.v1.routers.prescription_router import router
from app.domain.entities.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.domain.entities.consultation import Consultation
from app.domain.entities.prescription import (
    Prescription,
    PrescriptionItem,
    PrescriptionReminder,
    PrescriptionTreatment,
)


def _prescription() -> Prescription:
    return Prescription(
        id=1,
        consultation_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        veterinarian_id=1,
        diagnosis="Otitis externa",
        treatment_notes="Limpiar oido a diario",
        created_by=None,
        items=[
            PrescriptionItem(
                id=1,
                name="Otinorm",
                dosage="1 gota",
                frequency="3x dia",
                duration="7 dias",
            )
        ],
        treatments=[
            PrescriptionTreatment(
                id=1, name="Limpiado auricular", instructions="con gasa"
            )
        ],
        reminders=[
            PrescriptionReminder(
                id=1,
                title="Revisar curacion",
                due_at=datetime(2026, 9, 1),
                note="si empeora",
            )
        ],
    )


def _consultation() -> Consultation:
    return Consultation(
        id=1,
        appointment_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        veterinarian_id=1,
        history="...",
        diagnosis="Otitis",
        recommendations="...",
    )


def _appointment(status: AppointmentStatus) -> Appointment:
    from datetime import timedelta

    now = datetime(2026, 8, 20)
    return Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=now,
        scheduled_end=now + timedelta(minutes=30),
        status=status,
    )


@pytest_asyncio.fixture
async def app_ctx():  # noqa: C901
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/v1")

    mock_prescription_repo = AsyncMock()
    mock_consultation_repo = AsyncMock()
    mock_appointment_repo = AsyncMock()
    mock_pet_repo = MagicMock()
    mock_owner_repo = MagicMock()
    mock_internal_user_repo = AsyncMock()
    mock_internal_user_repo.get_by_user_id = AsyncMock(return_value=None)

    async def get_mock_user():
        return {"user_id": 10, "clinic_id": 1, "role": "veterinarian"}

    def get_mock_prescription_repo():
        return mock_prescription_repo

    def get_mock_consultation_repo():
        return mock_consultation_repo

    def get_mock_appointment_repo():
        return mock_appointment_repo

    def get_mock_pet_repo():
        return mock_pet_repo

    def get_mock_owner_repo():
        return mock_owner_repo

    def get_mock_internal_user_repo():
        return mock_internal_user_repo

    async def get_mock_db():
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

        yield _S()

    test_app.dependency_overrides[rx.get_current_db] = get_mock_db
    test_app.dependency_overrides[rx.get_current_access_user] = get_mock_user
    test_app.dependency_overrides[rx.get_prescription_repo] = get_mock_prescription_repo
    test_app.dependency_overrides[rx.get_consultation_repo] = get_mock_consultation_repo
    test_app.dependency_overrides[rx.get_appointment_repo] = get_mock_appointment_repo
    test_app.dependency_overrides[rx.get_pet_repo] = get_mock_pet_repo
    test_app.dependency_overrides[rx.get_owner_repo] = get_mock_owner_repo
    test_app.dependency_overrides[rx.get_internal_user_repo] = (
        get_mock_internal_user_repo
    )

    yield {
        "app": test_app,
        "prescription_repo": mock_prescription_repo,
        "consultation_repo": mock_consultation_repo,
        "appointment_repo": mock_appointment_repo,
        "pet_repo": mock_pet_repo,
    }
    test_app.dependency_overrides.clear()


def _payload() -> dict:
    return {
        "consultation_id": 1,
        "pet_id": 1,
        "diagnosis": "Otitis externa",
        "treatment_notes": "Limpiar oido a diario",
        "items": [
            {
                "name": "Otinorm",
                "dosage": "1 gota",
                "frequency": "3x dia",
                "duration": "7 dias",
            }
        ],
        "treatments": [{"name": "Limpiado auricular", "instructions": "con gasa"}],
        "reminders": [
            {
                "title": "Revisar curacion",
                "due_at": "2026-09-01T00:00:00",
                "note": "si empeora",
            }
        ],
    }


class TestPrescriptionCreate:
    @pytest.mark.asyncio
    async def test_c1_create_ok(self, app_ctx):
        a = app_ctx
        a["consultation_repo"].get_by_id = AsyncMock(return_value=_consultation())
        a["appointment_repo"].get_by_id = AsyncMock(
            return_value=_appointment(AppointmentStatus.COMPLETED)
        )
        a["prescription_repo"].exists_by_consultation = AsyncMock(return_value=False)
        a["prescription_repo"].create_prescription = AsyncMock(
            return_value=_prescription()
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=a["app"]), base_url="http://t"
        ) as c:
            r = await c.post("/api/v1/prescriptions", json=_payload())

        assert r.status_code == 201
        body = r.json()
        assert body["diagnosis"] == "Otitis externa"
        assert len(body["items"]) == 1
        assert len(body["treatments"]) == 1
        assert len(body["reminders"]) == 1

    @pytest.mark.asyncio
    async def test_c2_consultation_missing_422(self, app_ctx):
        a = app_ctx
        a["consultation_repo"].get_by_id = AsyncMock(return_value=None)
        a["prescription_repo"].create_prescription = AsyncMock(
            return_value=_prescription()
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=a["app"]), base_url="http://t"
        ) as c:
            r = await c.post("/api/v1/prescriptions", json=_payload())

        assert r.status_code == 422
        # Sin registro parcial: create_prescription nunca debe llamarse.
        a["prescription_repo"].create_prescription.assert_not_called()

    @pytest.mark.asyncio
    async def test_c3_consultation_not_completed_422(self, app_ctx):
        a = app_ctx
        a["consultation_repo"].get_by_id = AsyncMock(return_value=_consultation())
        a["appointment_repo"].get_by_id = AsyncMock(
            return_value=_appointment(AppointmentStatus.CONFIRMED)
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=a["app"]), base_url="http://t"
        ) as c:
            r = await c.post("/api/v1/prescriptions", json=_payload())

        assert r.status_code == 422
        a["prescription_repo"].create_prescription.assert_not_called()

    @pytest.mark.asyncio
    async def test_c4_duplicate_409(self, app_ctx):
        a = app_ctx
        a["consultation_repo"].get_by_id = AsyncMock(return_value=_consultation())
        a["appointment_repo"].get_by_id = AsyncMock(
            return_value=_appointment(AppointmentStatus.COMPLETED)
        )
        a["prescription_repo"].exists_by_consultation = AsyncMock(return_value=True)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=a["app"]), base_url="http://t"
        ) as c:
            r = await c.post("/api/v1/prescriptions", json=_payload())

        assert r.status_code == 409
        a["prescription_repo"].create_prescription.assert_not_called()
