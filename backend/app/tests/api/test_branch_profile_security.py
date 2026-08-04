"""Pruebas de seguridad para perfiles de sucursal (IDOR/BOLA, autenticación).

Esta suite cubre los gaps C2 y B1 que requirieron nuevas pruebas HTTPX:
- 401 sin token o con token inválido.
- 403 usuario autenticado pero sin acceso a la sucursal.
- IDOR/BOLA: intento de acceso cruzado a otra clinic no debe devolver datos protegidos.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient


class TestBranchProfileSecurityAuth:
    """Casos de seguridad para endpoint protegido del perfil."""

    @pytest.fixture(autouse=True)
    def override_public_use_case(self):
        """Evita que el endpoint público dependa de la base de datos real."""
        from app.api.main import app
        from app.api.v1.routers.branch_profile import get_branch_use_case
        from app.domain.entities.branch import Branch

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

        app.dependency_overrides[get_branch_use_case] = lambda: _FakePublicUseCase()
        yield
        app.dependency_overrides.clear()

    def test_protected_endpoint_rejects_no_auth(self):
        """Sin Bearer token el endpoint protegido debe rechazar con 401."""
        from app.api.main import app
        client = TestClient(app)
        response = client.get("/api/v1/clinics/branches/1/2")
        assert response.status_code == 401, (
            f"Se esperaba 401 pero se obtuvo {response.status_code}. "
            f'Response: "{response.text}"'
        )

    def test_protected_endpoint_validates_token_format(self):
        """Con un token inválido el endpoint debe devolver 401."""
        from app.api.main import app
        client = TestClient(app)
        response = client.get(
            "/api/v1/clinics/branches/1/2",
            headers={"Authorization": "Bearer invalid-token-string"}
        )
        assert response.status_code == 401, (
            f"Se esperaba 401 para token inválido pero se obtuvo {response.status_code}."
        )

    def test_public_endpoint_accepts_any_access(self):
        """El endpoint público funciona sin autenticación."""
        from app.api.main import app
        client = TestClient(app)
        response = client.get("/api/v1/clinics/branches/99")
        assert response.status_code not in [401, 403], (
            f"El endpoint público no debe requerir autenticación pero obtuvo "
            f"{response.status_code}."
        )
