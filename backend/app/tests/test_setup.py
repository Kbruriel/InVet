"""Tests para verificar la configuración básica de la aplicación."""

from fastapi.testclient import TestClient

from app.api.main import app
from app.core.config import settings

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "InVet Backend API"}


def test_app_creation():
    assert app is not None
    assert app.title == "InVet"


def test_api_v1_str():
    assert settings.API_V1_STR == "/api/v1"


def test_database_config():
    assert settings.POSTGRES_SERVER == "localhost"
    assert settings.POSTGRES_USER == "postgres"
    assert settings.POSTGRES_DB == "invet"


def test_qa_env_file_is_supported():
    env_files = settings.model_config.get("env_file")

    assert env_files is not None
    assert ".env.qa" in env_files
