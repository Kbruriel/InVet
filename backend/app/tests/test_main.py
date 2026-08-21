"""Tests iniciales para verificar el arranque básico de la aplicación."""

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

import app.api.v1.routers.public_clinics as pub_clinics_mod
from app.api.main import app
from app.api.v1.schemas.public_clinic import (
    PublicClinicListDTO,
    PublicClinicsPaginatedResponse,
)
from app.core.config import settings

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "InVet Backend API"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_api_v1_root():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenido a la API InVet v1"}


def test_public_clinics_route_is_mounted_through_main_app():
    mock_use_case = MagicMock()
    mock_use_case.execute = AsyncMock(
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
            pagination={"page": 1, "size": 12, "total": 1, "total_pages": 1},
        )
    )

    app.dependency_overrides[
        pub_clinics_mod.get_public_clinic_list_use_case
    ] = lambda: mock_use_case
    try:
        response = client.get("/api/v1/clinicas?page=1&limit=12&size=12")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"][0]["name"] == "Clínica Test"
    mock_use_case.execute.assert_awaited_once_with(
        page=1,
        size=12,
        search=None,
        service_type=None,
    )


def test_public_routes_are_listed_in_openapi():
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

    paths = response.json()["paths"]
    assert "/api/v1/clinicas" in paths
    assert "/api/v1/sucursales" in paths
    assert "/api/v1/servicios" in paths


def test_project_name_config():
    assert settings.PROJECT_NAME == "InVet"
    assert settings.API_V1_STR == "/api/v1"
