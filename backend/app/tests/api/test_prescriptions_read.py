"""Read tests for prescription endpoints (BE-010, APIA-010 C8/C9)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.prescription_router as rx
from app.api.v1.routers.prescription_router import router
from app.domain.entities.prescription import (
    Prescription,
    PrescriptionItem,
    PrescriptionReminder,
    PrescriptionTreatment,
)


def _prescription(prescription_id: int = 8, pet_id: int = 9) -> Prescription:
    return Prescription(
        id=prescription_id,
        consultation_id=1,
        pet_id=pet_id,
        clinic_id=1,
        branch_id=1,
        veterinarian_id=1,
        diagnosis="Fiebre canina",
        treatment_notes="Descansar 3 dias",
        created_by=5,
        items=[
            PrescriptionItem(
                id=1,
                name="Antifloxac",
                dosage="250 mg",
                frequency="1/12h",
                duration="5 dias",
            )
        ],
        treatments=[
            PrescriptionTreatment(
                id=1, name="Fisioterapia", instructions="3 sesiones/semana"
            )
        ],
        reminders=[
            PrescriptionReminder(
                id=1, title="Control semana 1", due_at=datetime(2026, 9, 5), note=None
            )
        ],
    )


def _make_app(role: str = "owner", clinic_id: int = 1):
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    mock_prescription_repo = AsyncMock()
    mock_pet_repo = MagicMock()
    mock_owner_repo = MagicMock()

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
    app.dependency_overrides[rx.get_pet_repo] = lambda: mock_pet_repo
    app.dependency_overrides[rx.get_owner_repo] = lambda: mock_owner_repo

    return app, mock_prescription_repo, mock_pet_repo, mock_owner_repo


class TestPrescriptionRead:
    @pytest.mark.asyncio
    async def test_c8_detail_ok(self):
        app, p_repo, pet_repo, owner_repo = _make_app(role="owner")
        # El owner tiene la mascota pet_id=9.
        owner_repo.get_owner_by_user_id.return_value = MagicMock(id=99)
        p_repo.get_by_id = AsyncMock(
            return_value=_prescription(prescription_id=8, pet_id=9)
        )
        pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=99)

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions/8")

        assert r.status_code == 200
        body = r.json()
        assert body["id"] == 8
        assert body["diagnosis"] == "Fiebre canina"
        assert len(body["items"]) == 1
        assert body["items"][0]["name"] == "Antifloxac"
        assert len(body["treatments"]) == 1
        assert len(body["reminders"]) == 1

    @pytest.mark.asyncio
    async def test_c8_detail_ok_vet_same_clinic(self):
        app, p_repo, pet_repo, owner_repo = _make_app(role="veterinarian")
        # Sin owner -> no check de ownership extra.
        owner_repo.get_owner_by_user_id.return_value = None
        p_repo.get_by_id = AsyncMock(
            return_value=_prescription(prescription_id=8, pet_id=9)
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions/8")

        assert r.status_code == 200
        assert r.json()["id"] == 8

    @pytest.mark.asyncio
    async def test_c9_list_ok(self):
        app, p_repo, pet_repo, owner_repo = _make_app(role="owner")
        owner_repo.get_owner_by_user_id.return_value = MagicMock(id=99)
        # pet_id=9 es del owner 99.
        pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=99)
        items = [_prescription(prescription_id=i, pet_id=9) for i in (8, 7)]
        p_repo.list_by_pet = AsyncMock(return_value=(items, 2))

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get(
                "/api/v1/prescriptions",
                params={"pet_id": 9, "page": 1, "page_size": 20},
            )

        assert r.status_code == 200
        body = r.json()
        assert len(body["items"]) == 2
        assert body["meta"]["page"] == 1
        assert body["meta"]["page_size"] == 20
        assert body["meta"]["total"] == 2
        assert body["meta"]["pages"] == 1

    @pytest.mark.asyncio
    async def test_c9_pagination_meta_consistency(self):
        app, p_repo, pet_repo, owner_repo = _make_app(role="owner")
        owner_repo.get_owner_by_user_id.return_value = MagicMock(id=99)
        pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=99)
        p_repo.list_by_pet = AsyncMock(return_value=([], 42))

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get(
                "/api/v1/prescriptions",
                params={"pet_id": 9, "page": 1, "page_size": 10},
            )

        assert r.status_code == 200
        body = r.json()
        assert body["meta"]["page_size"] == 10
        assert body["meta"]["total"] == 42
        assert body["meta"]["pages"] == 5  # ceil(42/10)
        assert "size" in body["meta"]
