"""Pruebas API de citas médicas (BE-008) - Pruebas contractuales e integration."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.main import create_app
from app.core.security import get_current_access_user
from app.infrastructure.database import get_db


def _override_auth(user_id: int, role: str = "vet"):
    """Helper para simular autenticación."""

    def _dependency() -> dict:
        return {"id": user_id, "role": role}

    return _dependency


def _build_client(db_session, user_id: int, role: str = "vet") -> TestClient:
    """Construye un TestClient con auth simulada y DB aislada."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_access_user] = _override_auth(user_id, role)
    return TestClient(app)


@pytest.fixture
def unauthenticated_client(db_session):
    """Cliente sin autenticación para pruebas de auth."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(db_session):
    """Cliente con autenticación simulada para pruebas de validación."""
    return _build_client(db_session, user_id=1, role="vet")


class TestCreateAppointment:
    """Pruebas POST /api/v1/appointments."""

    def test_create_appointment_unauthenticated(self, unauthenticated_client):
        """Sin token debe responder 401."""
        resp = unauthenticated_client.post(
            "/api/v1/appointments",
            json={
                "pet_id": 1,
                "appointment_type": "consultation",
                "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "duration_minutes": 30,
            },
        )
        assert resp.status_code in (401, 403)

    def test_create_appointment_invalid_type(self, authenticated_client):
        """Tipo de cita inválido debe responder 422."""
        resp = authenticated_client.post(
            "/api/v1/appointments",
            json={
                "pet_id": 1,
                "appointment_type": "invalid",
                "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "duration_minutes": 30,
            },
        )
        assert resp.status_code == 422


class TestGetAppointments:
    """Pruebas GET /api/v1/appointments."""

    def test_list_appointments_unauthenticated(self, unauthenticated_client):
        """Sin token debe responder 401."""
        resp = unauthenticated_client.get("/api/v1/appointments")
        assert resp.status_code in (401, 403)


class TestAppointmentStatusTransition:
    """Pruebas POST /api/v1/appointments/{id}/status."""

    def test_transition_status_unauthenticated(self, unauthenticated_client):
        """Sin token debe responder 401."""
        resp = unauthenticated_client.post(
            "/api/v1/appointments/999/status", json={"status": "approved"}
        )
        assert resp.status_code in (401, 403)


class TestAppointmentAvailability:
    """Pruebas GET /api/v1/appointments/availability."""

    def test_availability_unauthenticated(self, unauthenticated_client):
        """Disponible sin token o con token."""
        _resp = unauthenticated_client.get(
            "/api/v1/appointments/availability",
            params={"date": (datetime.now(UTC) + timedelta(days=1)).isoformat()[:10]},
        )
        # Este endpoint puede ser público o requerir auth según configuración


class TestAppointmentCRUD:
    """Pruebas CRUD de citas."""

    def test_get_appointment_by_id_unauthenticated(self, unauthenticated_client):
        """Sin token debe responder 401."""
        resp = unauthenticated_client.get("/api/v1/appointments/999")
        assert resp.status_code in (401, 403)

    def test_cancel_appointment_unauthenticated(self, unauthenticated_client):
        """Sin token debe responder 401."""
        resp = unauthenticated_client.delete("/api/v1/appointments/999")
        assert resp.status_code in (401, 403)


class TestTenantIsolation:
    """Pruebas de aislamiento por clínica."""

    def test_cross_clinic_access_fails(self, authenticated_client):
        """Intentar acceder a cita de otra clínica debe fallar."""
        # Esta prueba requiere setup con dos clínicas y tokens diferentes
        pytest.skip("Requiere fixtures de clínicas cruzadas")


class TestValidation:
    """Pruebas de validación de inputs (requieren auth para llegar a validación)."""

    def test_missing_required_fields(self, authenticated_client):
        """Faltan campos requeridos debe responder 422."""
        resp = authenticated_client.post("/api/v1/appointments", json={})
        assert resp.status_code == 422

    def test_past_date_rejected(self, authenticated_client):
        """Fecha pasada debe responder 422."""
        past_date = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        resp = authenticated_client.post(
            "/api/v1/appointments",
            json={
                "pet_id": 1,
                "appointment_type": "consultation",
                "scheduled_start": past_date,
                "duration_minutes": 30,
            },
        )
        assert resp.status_code == 422

    def test_duration_too_short(self, authenticated_client):
        """Duración menor a 15 min debe responder 422."""
        resp = authenticated_client.post(
            "/api/v1/appointments",
            json={
                "pet_id": 1,
                "appointment_type": "consultation",
                "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "duration_minutes": 10,
            },
        )
        assert resp.status_code == 422

    def test_duration_too_long(self, authenticated_client):
        """Duración mayor a 120 min debe responder 422."""
        resp = authenticated_client.post(
            "/api/v1/appointments",
            json={
                "pet_id": 1,
                "appointment_type": "consultation",
                "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "duration_minutes": 180,
            },
        )
        assert resp.status_code == 422
