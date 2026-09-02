"""Contract tests for public branches endpoint using async TestClient."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import app.api.v1.routers.public_branches as pub_branches_mod
from app.api.v1.routers.public_branches import router
from app.api.v1.schemas.public_branch import (
    PublicBranchesPaginatedResponse,
    PublicBranchListDTO,
)
from app.application.use_cases.public_branches import ListPublicBranchesUseCase


@pytest.fixture
def mock_use_case():
    use_case = MagicMock(spec=ListPublicBranchesUseCase)
    use_case.execute = AsyncMock(
        return_value=PublicBranchesPaginatedResponse(
            data=[
                PublicBranchListDTO(
                    id=1,
                    clinic_id=1,
                    name="Sucursal Test",
                    description="Descripción de prueba",
                    city="Ciudad Test",
                    address="Calle Test 456",
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

    app.dependency_overrides[pub_branches_mod.get_public_branch_list_use_case] = (
        mock_get_use_case
    )

    yield app

    app.dependency_overrides.clear()


class TestListSucursales:
    @pytest.mark.asyncio
    async def test_list_sucursales_returns_200(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/sucursales?page=1&size=20")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data and "pagination" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Sucursal Test"
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["total"] == 1

    @pytest.mark.asyncio
    async def test_list_sucursales_with_clinica_id_filter(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/sucursales?clinica_id=5&page=1&size=20")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1

    @pytest.mark.asyncio
    async def test_list_sucursales_validates_page_size(self):
        app = FastAPI()
        app.include_router(router)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/sucursales?page=1&size=0")
            assert response.status_code == 422
            response = await client.get("/sucursales?page=1&size=101")
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_public_branch_dto_does_not_expose_sensitive_fields(self, async_app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=async_app), base_url="http://test"
        ) as client:
            response = await client.get("/sucursales?page=1&size=20")
            data = response.json()
        assert "email" not in data["data"][0]
        assert "phone" not in data["data"][0]
        assert "postal_code" not in data["data"][0]
        assert "created_at" not in data["data"][0]
        assert "updated_at" not in data["data"][0]
