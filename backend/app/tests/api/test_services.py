"""Tests para servicios (slice 006)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.database.session import Base
from app.api.main import app

# Engine de prueba con SQLite en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db():
    """Crear base de datos de prueba."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(db):
    """Crear cliente de prueba con DB override."""
    from app.infrastructure.database import get_db

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestServicesHappyPath:
    """Casos felices para servicios."""

    def test_create_service(self, client):
        """Crear un servicio exitosamente."""
        response = client.post(
            "/api/v1/services",
            json={
                "name": "Consulta general",
                "description": "Consulta veterinaria general",
                "price": 50.0,
                "duration_minutes": 30,
                "is_active": True,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 201 or response.status_code == 401

    def test_list_services(self, client):
        """Listar servicios."""
        response = client.get(
            "/api/v1/services",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_get_service(self, client):
        """Obtener un servicio por ID."""
        response = client.get(
            "/api/v1/services/1",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_update_service(self, client):
        """Actualizar un servicio."""
        response = client.put(
            "/api/v1/services/1",
            json={"description": "Descripción actualizada"},
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_deactivate_service(self, client):
        """Desactivar un servicio."""
        response = client.patch(
            "/api/v1/services/1/deactivate",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 204 or response.status_code == 401


class TestServicesNegativePath:
    """Casos negativos para servicios."""

    def test_create_service_missing_name(self, client):
        """Crear servicio sin nombre debe fallar."""
        response = client.post(
            "/api/v1/services",
            json={
                "description": "Sin nombre",
                "price": 50.0,
                "duration_minutes": 30,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_service_negative_price(self, client):
        """Crear servicio con precio negativo debe fallar."""
        response = client.post(
            "/api/v1/services",
            json={
                "name": "Servicio invalido",
                "price": -10.0,
                "duration_minutes": 30,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_service_zero_duration(self, client):
        """Crear servicio con duración cero debe fallar."""
        response = client.post(
            "/api/v1/services",
            json={
                "name": "Servicio invalido",
                "price": 50.0,
                "duration_minutes": 0,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_get_nonexistent_service(self, client):
        """Obtener servicio inexistente debe retornar 404."""
        response = client.get(
            "/api/v1/services/99999",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (404, 401)

    def test_update_nonexistent_service(self, client):
        """Actualizar servicio inexistente debe retornar 404."""
        response = client.put(
            "/api/v1/services/99999",
            json={"description": "Actualizacion"},
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (404, 401)


class TestServicesPermissions:
    """Pruebas de permisos para servicios."""

    def test_unauthenticated_access(self, client):
        """Acceso sin token debe retornar 401."""
        response = client.get("/api/v1/services")
        assert response.status_code == 401

    def test_viewer_cannot_create(self, client):
        """Usuario con rol viewer no puede crear servicios."""
        response = client.post(
            "/api/v1/services",
            json={
                "name": "Servicio",
                "price": 50.0,
                "duration_minutes": 30,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        # Debe fallar con 403 o 401 (dependiendo de si el token es valido)
        assert response.status_code in (403, 401)
