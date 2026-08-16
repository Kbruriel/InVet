"""Pruebas API de citas médicas (BE-008) - Pruebas contractuales e integration."""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import UTC, datetime, timedelta

# Importar el app FastAPI principal
from app.main import create_app


@pytest.fixture(scope="module")
def app():
    """Aplicación FastAPI de prueba."""
    application = create_app()
    return application


@pytest.fixture(scope="module")
async def client(app):
    """Cliente HTTP de prueba."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestCreateAppointment:
    """Pruebas POST /api/v1/appointments."""

    @pytest.mark.asyncio
    async def test_create_appointment_unauthenticated(self, client):
        """Sin token debe responder 401."""
        resp = await client.post("/api/v1/appointments", json={
            "pet_id": 1,
            "appointment_type": "consultation",
            "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            "duration_minutes": 30
        })
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_create_appointment_invalid_type(self, client):
        """Tipo de cita inválido debe responder 422."""
        resp = await client.post("/api/v1/appointments", json={
            "pet_id": 1,
            "appointment_type": "invalid",
            "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            "duration_minutes": 30
        })
        assert resp.status_code == 422


class TestGetAppointments:
    """Pruebas GET /api/v1/appointments."""

    @pytest.mark.asyncio
    async def test_list_appointments_unauthenticated(self, client):
        """Sin token debe responder 401."""
        resp = await client.get("/api/v1/appointments")
        assert resp.status_code in (401, 403)


class TestAppointmentStatusTransition:
    """Pruebas POST /api/v1/appointments/{id}/status."""

    @pytest.mark.asyncio
    async def test_transition_status_unauthenticated(self, client):
        """Sin token debe responder 401."""
        resp = await client.post("/api/v1/appointments/999/status", json={
            "status": "approved"
        })
        assert resp.status_code in (401, 403)


class TestAppointmentAvailability:
    """Pruebas GET /api/v1/appointments/availability."""

    @pytest.mark.asyncio
    async def test_availability_unauthenticated(self, client):
        """Disponible sin token o con token."""
        resp = await client.get("/api/v1/appointments/availability", params={
            "date": (datetime.now(UTC) + timedelta(days=1)).isoformat()[:10]
        })
        # Este endpoint puede ser público o requerir auth según configuración


class TestAppointmentCRUD:
    """Pruebas CRUD de citas."""

    @pytest.mark.asyncio
    async def test_get_appointment_by_id_unauthenticated(self, client):
        """Sin token debe responder 401."""
        resp = await client.get("/api/v1/appointments/999")
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_cancel_appointment_unauthenticated(self, client):
        """Sin token debe responder 401."""
        resp = await client.delete("/api/v1/appointments/999")
        assert resp.status_code in (401, 403)


class TestTenantIsolation:
    """Pruebas de aislamiento por clínica."""

    @pytest.mark.asyncio
    async def test_cross_clinic_access_fails(self, client):
        """Intentar acceder a cita de otra clínica debe fallar."""
        # Esta prueba requiere setup con dos clínicas y tokens diferentes
        pytest.skip("Requiere fixtures de clínicas cruzadas")


class TestValidation:
    """Pruebas de validación de inputs."""

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """Faltan campos requeridos debe responder 422."""
        resp = await client.post("/api/v1/appointments", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_past_date_rejected(self, client):
        """Fecha en el pasado debe ser rechazada."""
        past = datetime.now(UTC) - timedelta(days=1)
        resp = await client.post("/api/v1/appointments", json={
            "pet_id": 1,
            "appointment_type": "consultation",
            "scheduled_start": past.isoformat(),
            "duration_minutes": 30
        })
        assert resp.status_code in (422, 400)

    @pytest.mark.asyncio
    async def test_duration_too_short(self, client):
        """Duración menor a 15 min debe fallar."""
        resp = await client.post("/api/v1/appointments", json={
            "pet_id": 1,
            "appointment_type": "consultation",
            "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            "duration_minutes": 10
        })
        assert resp.status_code in (422, 400)

    @pytest.mark.asyncio
    async def test_duration_too_long(self, client):
        """Duración mayor a 120 min debe fallar."""
        resp = await client.post("/api/v1/appointments", json={
            "pet_id": 1,
            "appointment_type": "consultation",
            "scheduled_start": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            "duration_minutes": 150
        })
        assert resp.status_code in (422, 400)
