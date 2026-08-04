"""Pruebas API para perfiles de clínica/sucursal."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.v1.routers.branch_profile import (
    get_branch_protected_use_case,
    get_branch_use_case,
)
from app.domain.entities.branch import Branch


@pytest.fixture(scope="module")
def client():
    """Crea un cliente de prueba para la aplicación FastAPI."""

    class _FakePublicUseCase:
        async def execute(self, branch_id: int):
            return Branch(
                id=branch_id,
                clinic_id=1,
                name="Clinica Test",
                description="Perfil de prueba",
                address="Calle 123",
                city="Ciudad Test",
                state="Estado Test",
                country="MX",
                postal_code="12345",
                phone=None,
                email=None,
                is_active=True,
                created_at=datetime(2024, 1, 1, 0, 0, 0),
                updated_at=datetime(2024, 1, 1, 0, 0, 0),
            )

    class _FakeProtectedUseCase:
        async def execute(self, branch_id: int, clinic_id: int, current_user: dict):
            return Branch(
                id=branch_id,
                clinic_id=clinic_id,
                name="Clinica Test",
                description="Perfil protegido de prueba",
                address="Calle 123",
                city="Ciudad Test",
                state="Estado Test",
                country="MX",
                postal_code="12345",
                phone=None,
                email=None,
                is_active=True,
                created_at=datetime(2024, 1, 1, 0, 0, 0),
                updated_at=datetime(2024, 1, 1, 0, 0, 0),
            )

    app.dependency_overrides[get_branch_use_case] = _FakePublicUseCase
    app.dependency_overrides[get_branch_protected_use_case] = _FakeProtectedUseCase

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class TestBranchProfileAPI:
    """Test para endpoints de perfil de clínica/sucursal."""

    def test_get_branch_public_profile_success(self, client):
        """Prueba obtener perfil público exitoso."""
        response = client.get("/api/v1/clinics/branches/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_branch_protected_profile_success(self, client):
        """Prueba obtener perfil protegido exitoso."""
        response = client.get("/api/v1/clinics/branches/1/1")
        assert response.status_code == 401
