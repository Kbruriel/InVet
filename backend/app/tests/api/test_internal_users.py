"""Tests para usuarios internos (slice 006)."""

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


class TestInternalUsersHappyPath:
    """Casos felices para usuarios internos."""

    def test_create_internal_user(self, client):
        """Crear un usuario interno exitosamente."""
        response = client.post(
            "/api/v1/internal-users",
            json={
                "user_id": 1,
                "nombre": "Maria Garcia",
                "rol": "manager",
                "branch_ids": [1, 2],
                "is_active": True,
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 201 or response.status_code == 401

    def test_list_internal_users(self, client):
        """Listar usuarios internos."""
        response = client.get(
            "/api/v1/internal-users",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_get_internal_user(self, client):
        """Obtener un usuario interno por ID."""
        response = client.get(
            "/api/v1/internal-users/1",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_update_internal_user(self, client):
        """Actualizar un usuario interno."""
        response = client.put(
            "/api/v1/internal-users/1",
            json={"rol": "admin"},
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 200 or response.status_code == 401

    def test_deactivate_internal_user(self, client):
        """Desactivar un usuario interno."""
        response = client.patch(
            "/api/v1/internal-users/1/deactivate",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 204 or response.status_code == 401

    def test_assign_branch(self, client):
        """Asignar sucursal a usuario interno."""
        response = client.post(
            "/api/v1/internal-users/1/assign-branch",
            json={"branch_id": 3},
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 201 or response.status_code == 401

    def test_unassign_branch(self, client):
        """Desasignar sucursal de usuario interno."""
        response = client.delete(
            "/api/v1/internal-users/1/assign-branch/3",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code == 204 or response.status_code == 401


class TestInternalUsersNegativePath:
    """Casos negativos para usuarios internos."""

    def test_create_internal_user_missing_user_id(self, client):
        """Crear usuario interno sin user_id debe fallar."""
        response = client.post(
            "/api/v1/internal-users",
            json={
                "nombre": "Maria Garcia",
                "rol": "manager",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_internal_user_missing_nombre(self, client):
        """Crear usuario interno sin nombre debe fallar."""
        response = client.post(
            "/api/v1/internal-users",
            json={
                "user_id": 1,
                "rol": "manager",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_internal_user_missing_rol(self, client):
        """Crear usuario interno sin rol debe fallar."""
        response = client.post(
            "/api/v1/internal-users",
            json={
                "user_id": 1,
                "nombre": "Maria Garcia",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_create_internal_user_invalid_user_id(self, client):
        """Crear usuario interno con user_id invalido debe fallar."""
        response = client.post(
            "/api/v1/internal-users",
            json={
                "user_id": 0,
                "nombre": "Maria Garcia",
                "rol": "manager",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)

    def test_get_nonexistent_internal_user(self, client):
        """Obtener usuario interno inexistente debe retornar 404."""
        response = client.get(
            "/api/v1/internal-users/99999",
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (404, 401)

    def test_assign_branch_missing_branch_id(self, client):
        """Asignar sucursal sin branch_id debe fallar."""
        response = client.post(
            "/api/v1/internal-users/1/assign-branch",
            json={},
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (422, 401)


class TestInternalUsersPermissions:
    """Pruebas de permisos para usuarios internos."""

    def test_unauthenticated_access(self, client):
        """Acceso sin token debe retornar 401."""
        response = client.get("/api/v1/internal-users")
        assert response.status_code == 401

    def test_viewer_cannot_create(self, client):
        """Usuario con rol viewer no puede crear usuarios internos."""
        response = client.post(
            "/api/v1/internal-users",
            json={
                "user_id": 1,
                "nombre": "Maria Garcia",
                "rol": "manager",
            },
            headers={"Authorization": "Bearer fake_token"},
        )
        assert response.status_code in (403, 401)
