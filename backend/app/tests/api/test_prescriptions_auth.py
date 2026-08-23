"""Auth tests for prescription endpoints (BE-010, APIA-010 C5: sin token -> 401)."""

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.prescription_router as rx
from app.api.v1.routers.prescription_router import router

# NO se sobreescribe get_current_access_user: el oauth2_scheme real exige un
# token Bearer y responde 401 si no hay cabecera Authorization.


def _make_app():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

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

    # Se sobreescriben SOLO los repos/db para evitar tocar la base de datos;
    # la autenticacion real (oauth2) permanece activa para forzar el 401.
    app.dependency_overrides[rx.get_current_db] = fake_db
    app.dependency_overrides[rx.get_prescription_repo] = lambda: object()
    app.dependency_overrides[rx.get_consultation_repo] = lambda: object()
    app.dependency_overrides[rx.get_appointment_repo] = lambda: object()
    app.dependency_overrides[rx.get_pet_repo] = lambda: object()
    app.dependency_overrides[rx.get_owner_repo] = lambda: object()
    app.dependency_overrides[rx.get_internal_user_repo] = lambda: object()
    return app


class TestPrescriptionAuth:
    @pytest.mark.asyncio
    async def test_c5_post_without_token_401(self):
        app = _make_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.post(
                "/api/v1/prescriptions",
                json={"consultation_id": 1, "pet_id": 1, "diagnosis": "x"},
            )
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_c5_get_detail_without_token_401(self):
        app = _make_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions/1")
        assert r.status_code == 401

    @pytest.mark.asyncio
    async def test_c5_get_list_without_token_401(self):
        app = _make_app()
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://t"
        ) as c:
            r = await c.get("/api/v1/prescriptions", params={"pet_id": 1})
        assert r.status_code == 401
