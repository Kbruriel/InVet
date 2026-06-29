"""Tests iniciales para verificar el arranque básico de la aplicación."""
from fastapi.testclient import TestClient

from app.api.main import app
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


def test_project_name_config():
    assert settings.PROJECT_NAME == "InVet"
    assert settings.API_V1_STR == "/api/v1"
