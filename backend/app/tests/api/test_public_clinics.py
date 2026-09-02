"""Contract tests for public clinics endpoint using async TestClient."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import app.api.v1.routers.public_clinics as pub_clinics_mod
from app.api.v1.routers.public_clinics import router
from app.api.v1.schemas.public_clinic import (
    PublicClinicDetailDTO,
    PublicClinicListDTO,
    PublicClinicsPaginatedResponse,
)
from app.application.use_cases.public_clinics import ListPublicClinicsUseCase


@pytest.fixture
def mock_use_case():
    use_case = MagicMock(spec=ListPublicClinicsUseCase)
    use_case.execute = AsyncMock(
        return_value=PublicClinicsPaginatedResponse(
            data=[
                PublicClinicListDTO(
                    id=1,
                    name="Clínica Test",
                    description="Descripción de prueba",
                    city="Ciudad Test",
                    address="Calle Test 123",
                    rating=None,
                )
            ],
            pagination={"page": 1, "size": 20, "total": 1, "total_pages": 1},
        )
    )
    use_case.get_by_id = AsyncMock(
        return_value=PublicClinicDetailDTO(
            id=1,
            name="Clínica Test",
            description="Descripción de prueba",
            city="Ciudad Test",
            address="Calle Test 123",
            rating=None,
            state="Estado Test",
            country="País Test",
            phone="1234567890",
        )
    )
    return use_case


@pytest_asyncio.fixture
async def async_app(mock_use_case):
    app = FastAPI()
    app.include_router(router)

    def mock_get_use_case():
        return mock_use_case

    app.dependency_overrides[pub_clinics_mod.get_public_clinic_list_use_case] = (
        mock_get_use_case
    )

    yield app

    app.dependency_overrides.clear()


class TestListClinicas:
    @pytest.mark.asyncio
    async def test_list_clinicas_returns_200(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/clinicas?page=1&size=20")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data and "pagination" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Clínica Test"
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total"] == 1

    @pytest.mark.asyncio
    async def test_list_clinicas_accepts_service_type_filter(
        self, async_app, mock_use_case
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/clinicas?page=1&size=20&service_type=estetica"
            )

        assert response.status_code == 200
        mock_use_case.execute.assert_awaited_once_with(
            page=1,
            size=20,
            search=None,
            service_type="estetica",
        )

    @pytest.mark.asyncio
    async def test_list_clinicas_validates_page_size(self):
        app = FastAPI()
        app.include_router(router)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/clinicas?page=1&size=0")
            assert response.status_code == 422
            response = await client.get("/clinicas?page=1&size=101")
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_clinicas_validates_page_number(self):
        app = FastAPI()
        app.include_router(router)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/clinicas?page=0&size=20")
            assert response.status_code == 422


class TestGetClinica:
    @pytest.mark.asyncio
    async def test_get_clinica_returns_200(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/clinicas/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1 and data["name"] == "Clínica Test"
        assert data["state"] == "Estado Test" and data["country"] == "País Test"

    @pytest.mark.asyncio
    async def test_get_clinica_returns_404_when_not_found(self):
        mock_use_case = MagicMock(spec=ListPublicClinicsUseCase)
        mock_use_case.get_by_id = AsyncMock(return_value=None)
        app = FastAPI()
        app.include_router(router)

        def mock_get_use_case():
            return mock_use_case

        app.dependency_overrides[pub_clinics_mod.get_public_clinic_list_use_case] = (
            mock_get_use_case
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/clinicas/999")
        assert response.status_code == 404
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_public_clinic_dto_does_not_expose_sensitive_fields(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/clinicas?page=1&size=20")
            data = response.json()
        assert "email" not in data["data"][0]
        assert "phone" not in data["data"][0]
        assert "postal_code" not in data["data"][0]
        assert "created_at" not in data["data"][0]
        assert "updated_at" not in data["data"][0]
