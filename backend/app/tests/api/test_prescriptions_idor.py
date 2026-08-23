"""IDOR / ownership tests for prescription endpoints (BE-010, APIA-010 C6/C7/C10)."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.prescription_router as rx
from app.api.v1.routers.prescription_router import router
from app.domain.entities.prescription import Prescription


def _prescription(pet_id: int = 1) -> Prescription:
    return Prescription(
        id=1,
        consultation_id=1,
        pet_id=pet_id,
        clinic_id=1,
        branch_id=1,
        veterinarian_id=1,
        diagnosis="Otitis externa",
        treatment_notes="...",
        items=[],
        treatments=[],
        reminders=[],
    )


def _make_app(role: str, clinic_id: int = 1):
    """Construye la app con overrides. Returns (app, ctx-dict)."""
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    mock_prescription_repo = AsyncMock()
    mock_consultation_repo = AsyncMock()
    mock_appointment_repo = AsyncMock()
    mock_pet_repo = MagicMock()
    mock_owner_repo = MagicMock()
    mock_internal_user_repo = AsyncMock()
    mock_internal_user_repo.get_by_user_id = AsyncMock(return_value=None)

    async def fake_user():
        return {"user_id": 99, "clinic_id": clinic_id, "role": role}

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

    async def fake_db():
        yield _S()

    app.dependency_overrides[rx.get_current_db] = fake_db
    app.dependency_overrides[rx.get_current_access_user] = fake_user
    app.dependency_overrides[rx.get_prescription_repo] = lambda: mock_prescription_repo
    app.dependency_overrides[rx.get_consultation_repo] = lambda: mock_consultation_repo
    app.dependency_overrides[rx.get_appointment_repo] = lambda: mock_appointment_repo
    app.dependency_overrides[rx.get_pet_repo] = lambda: mock_pet_repo
    app.dependency_overrides[rx.get_owner_repo] = lambda: mock_owner_repo
    app.dependency_overrides[rx.get_internal_user_repo] = (
        lambda: mock_internal_user_repo
    )

    ctx = {
        "app": app,
        "prescription_repo": mock_prescription_repo,
        "pet_repo": mock_pet_repo,
        "owner_repo": mock_owner_repo,
    }
    return app, ctx


def _payload() -> dict:
    return {
        "consultation_id": 1,
        "pet_id": 1,
        "diagnosis": "Otitis externa",
        "items": [{"name": "Otinorm"}],
        "treatments": [],
        "reminders": [],
    }


class TestPrescriptionIdor:
    @pytest.mark.asyncio
    async def test_c6_owner_cannot_create(self):
        app, ctx = _make_app(role="owner")
        ctx["owner_repo"].get_owner_by_user_id.return_value = None

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.post("/api/v1/prescriptions", json=_payload())

        assert r.status_code == 403
        ctx["prescription_repo"].create_prescription.assert_not_called()

    @pytest.mark.asyncio
    async def test_c7_foreign_vet_cannot_read(self):
        app, ctx = _make_app(role="veterinarian")
        # Tenant isolation: la receta no existe para la clinica del vet.
        ctx["prescription_repo"].get_by_id = AsyncMock(return_value=None)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions/1")

        assert r.status_code in (403, 404)

    @pytest.mark.asyncio
    async def test_c7_owner_cannot_read_foreign_pet(self):
        app, ctx = _make_app(role="owner")
        ctx["owner_repo"].get_owner_by_user_id.return_value = MagicMock(id=99)
        # La receta existe (mascota ajena, misma clinica).
        ctx["prescription_repo"].get_by_id = AsyncMock(
            return_value=_prescription(pet_id=1)
        )
        # La mascota NO pertenece al owner -> pet.owner_id = 42 != 99.
        ctx["pet_repo"].get_pet_by_id.return_value = MagicMock(owner_id=42)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions/1")

        assert r.status_code == 404

    @pytest.mark.asyncio
    async def test_c10_list_foreign_pet_denied(self):
        app, ctx = _make_app(role="owner")
        ctx["owner_repo"].get_owner_by_user_id.return_value = MagicMock(id=99)
        ctx["pet_repo"].get_pet_by_id.return_value = MagicMock(owner_id=42)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions", params={"pet_id": 1})

        assert r.status_code == 404
