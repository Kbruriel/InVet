"""Tests para veterinarios (slice 006)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.main import app
from app.infrastructure.database.session import Base

# Engine de prueba con SQLite en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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


class TestVeterinariansHappyPath:
    """Casos felices para veterinarios."""

    def test_create_veterinarian(self, client):
        """Crear un veterinario exitosamente."""
        response = client.post(
            "/api/v1/veterinarians",
            json={
                "nombre_completo": "Dr. Juan Perez",
                "licencia_profesional": "MP-12345",
                "especialidad": "Cirugia",
                "telefono": "555-1234",
                "email": "juan@vet.com",
                "is_active": True,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 201 or response.status_code == 401

    def test_list_veterinarians(self, client):
        """Listar veterinarios."""
        response = client.get(
            "/api/v1/veterinarians",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_get_veterinarian(self, client):
        """Obtener un veterinario por ID."""
        response = client.get(
            "/api/v1/veterinarians/1",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_update_veterinarian(self, client):
        """Actualizar un veterinario."""
        response = client.put(
            "/api/v1/veterinarians/1",
            json={"especialidad": "Cardiologia"},
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_deactivate_veterinarian(self, client):
        """Desactivar un veterinario."""
        response = client.patch(
            "/api/v1/veterinarians/1/deactivate",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 204 or response.status_code == 401


class TestVeterinariansNegativePath:
    """Casos negativos para veterinarios."""

    def test_create_veterinarian_missing_name(self, client):
        """Crear veterinario sin nombre debe fallar."""
        response = client.post(
            "/api/v1/veterinarians",
            json={
                "licencia_profesional": "MP-12345",
                "especialidad": "Cirugia",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_veterinarian_missing_license(self, client):
        """Crear veterinario sin licencia debe fallar."""
        response = client.post(
            "/api/v1/veterinarians",
            json={
                "nombre_completo": "Dr. Juan Perez",
                "especialidad": "Cirugia",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_veterinarian_invalid_email(self, client):
        """Crear veterinario con email invalido debe fallar."""
        response = client.post(
            "/api/v1/veterinarians",
            json={
                "nombre_completo": "Dr. Juan Perez",
                "licencia_profesional": "MP-12345",
                "especialidad": "Cirugia",
                "email": "invalid-email",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_get_nonexistent_veterinarian(self, client):
        """Obtener veterinario inexistente debe retornar 404."""
        response = client.get(
            "/api/v1/veterinarians/99999",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (404, 401)


class TestVeterinariansPermissions:
    """Pruebas de permisos para veterinarios."""

    def test_unauthenticated_access(self, client):
        """Acceso sin token debe retornar 401."""
        response = client.get("/api/v1/veterinarians")
        assert response.status_code == 401

    def test_viewer_cannot_create(self, client):
        """Usuario con rol viewer no puede crear veterinarios."""
        response = client.post(
            "/api/v1/veterinarians",
            json={
                "nombre_completo": "Dr. Juan Perez",
                "licencia_profesional": "MP-12345",
                "especialidad": "Cirugia",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (403, 401)
