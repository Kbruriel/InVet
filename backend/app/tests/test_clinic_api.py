"""Pruebas para los endpoints de clínicas y sucursales."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import (
    get_branch_profile_use_case,
    get_branch_profile_with_permission_use_case,
)
from app.api.main import app
from app.domain.entities.clinic import Branch, Rating, Schedule, Service


class FakePublicBranchProfileUseCase:
    async def execute(self, branch_id: int):
        return {
            "branch": {
                "id": branch_id,
                "clinic_id": 1,
                "name": "Sucursal Centro",
                "address": "Main Street 123",
                "city": "Ciudad",
                "state": "Estado",
                "country": "Pais",
                "postal_code": "12345",
                "phone": None,
                "email": "branch@example.com",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
            "services": [
                {
                    "id": 1,
                    "branch_id": branch_id,
                    "name": "Consulta General",
                    "description": "Consulta base",
                    "duration": 30,
                    "price": 250.0,
                    "is_active": True,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }
            ],
            "schedules": [
                {
                    "id": 1,
                    "branch_id": branch_id,
                    "day_of_week": 0,
                    "open_time": "09:00",
                    "close_time": "18:00",
                    "is_closed": False,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }
            ],
            "ratings_summary": {
                "average_rating": 5.0,
                "total_ratings": 1,
                "rating_distribution": {5: 1},
            },
        }


class FakeProtectedBranchProfileUseCase:
    async def execute(self, clinic_id: int, branch_id: int, user_id: int | None = None):
        return {
            "branch": {
                "id": branch_id,
                "clinic_id": clinic_id,
                "name": "Sucursal Centro",
                "address": "Main Street 123",
                "city": "Ciudad",
                "state": "Estado",
                "country": "Pais",
                "postal_code": "12345",
                "phone": None,
                "email": "branch@example.com",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            },
            "services": [],
            "schedules": [],
            "ratings_summary": {
                "average_rating": 0.0,
                "total_ratings": 0,
                "rating_distribution": {},
            },
        }


@pytest.fixture(autouse=True)
def override_branch_use_cases():
    app.dependency_overrides[get_branch_profile_use_case] = lambda: FakePublicBranchProfileUseCase()
    app.dependency_overrides[get_branch_profile_with_permission_use_case] = (
        lambda: FakeProtectedBranchProfileUseCase()
    )
    yield
    app.dependency_overrides.pop(get_branch_profile_use_case, None)
    app.dependency_overrides.pop(get_branch_profile_with_permission_use_case, None)


@pytest.mark.asyncio
async def test_get_branch_profile():
    """Public branch profile should return the stubbed payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clinics/branches/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["branch"]["id"] == 1
    assert payload["branch"]["name"] == "Sucursal Centro"
    assert payload["services"][0]["name"] == "Consulta General"
    assert payload["schedules"][0]["day_of_week"] == 0
    assert payload["ratings_summary"]["total_ratings"] == 1


@pytest.mark.asyncio
async def test_get_branch_profile_with_permissions_requires_auth():
    """Protected branch profile should require authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clinics/1/1")

    assert response.status_code == 401


def test_branch_entities():
    """Test de entidades de sucursal."""
    branch_data = {
        "id": 1,
        "clinic_id": 1,
        "name": "Clinica Veterinaria Central",
        "address": "Calle Principal 123",
        "city": "Ciudad Ejemplo",
        "state": "Estado Ejemplo",
        "country": "Pais Ejemplo",
        "postal_code": "12345",
        "phone": "+52 123 456 7890",
        "email": "contacto@clinica.com",
        "is_active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    branch = Branch(**branch_data)

    assert branch.id == 1
    assert branch.name == "Clinica Veterinaria Central"
    assert branch.is_active is True


def test_service_entity():
    """Test de entidad de servicio."""
    service_data = {
        "id": 1,
        "branch_id": 1,
        "name": "Consulta General",
        "description": "Servicio de consulta veterinaria basica",
        "duration": 30,
        "price": 250.0,
        "is_active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    service = Service(**service_data)

    assert service.id == 1
    assert service.name == "Consulta General"
    assert service.price == 250.0


def test_schedule_entity():
    """Test de entidad de horario."""
    schedule_data = {
        "id": 1,
        "branch_id": 1,
        "day_of_week": 0,
        "open_time": "09:00",
        "close_time": "18:00",
        "is_closed": False,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    schedule = Schedule(**schedule_data)

    assert schedule.id == 1
    assert schedule.day_of_week == 0
    assert schedule.open_time == "09:00"


def test_rating_entity():
    """Test de entidad de calificación."""
    rating_data = {
        "id": 1,
        "branch_id": 1,
        "user_id": 1,
        "rating": 5,
        "comment": "Excelente servicio",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    rating = Rating(**rating_data)

    assert rating.id == 1
    assert rating.rating == 5
    assert rating.comment == "Excelente servicio"
