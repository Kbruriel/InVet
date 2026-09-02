"""Contract tests for public services endpoint using async TestClient."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import app.api.v1.routers.public_services as pub_services_mod
from app.api.v1.routers.public_services import router
from app.api.v1.schemas.public_service import (
    PublicServiceListDTO,
    PublicServicesPaginatedResponse,
)
from app.application.use_cases.public_services import ListPublicServicesUseCase


@pytest.fixture
def mock_use_case():
    use_case = MagicMock(spec=ListPublicServicesUseCase)
    use_case.execute = AsyncMock(
        return_value=PublicServicesPaginatedResponse(
            data=[
                PublicServiceListDTO(
                    id=1,
                    name="Servicio Test",
                    description="Descripción de prueba",
                )
            ],
            pagination={"page": 1, "size": 20, "total": 1, "total_pages": 1},
        )
    )
    return use_case


@pytest_asyncio.fixture
async def async_app(mock_use_case):
    app = FastAPI()
    app.include_router(router)

    def mock_get_use_case():
        return mock_use_case

    app.dependency_overrides[pub_services_mod.get_public_service_list_use_case] = (
        mock_get_use_case
    )

    yield app

    app.dependency_overrides.clear()


class TestListServicios:
    @pytest.mark.asyncio
    async def test_list_servicios_returns_200(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/servicios?page=1&size=20")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data and "pagination" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Servicio Test"
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total"] == 1

    @pytest.mark.asyncio
    async def test_list_servicios_with_sucursal_id_filter(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/servicios?sucursal_id=5&page=1&size=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_servicios_with_clinica_id_filter(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/servicios?clinica_id=3&page=1&size=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_servicios_validates_page_size(self):
        app = FastAPI()
        app.include_router(router)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/servicios?page=1&size=0")
            assert response.status_code == 422
            response = await client.get("/servicios?page=1&size=101")
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_public_service_dto_does_not_expose_sensitive_fields(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/servicios?page=1&size=20")
            data = response.json()
        assert "email" not in data["data"][0]
        assert "phone" not in data["data"][0]
        assert "postal_code" not in data["data"][0]
        assert "created_at" not in data["data"][0]
        assert "updated_at" not in data["data"][0]
