"""Pruebas para los endpoints de clínicas y sucursales."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import (
    get_branch_admin_use_case,
    get_branch_hours_admin_use_case,
    get_branch_profile_use_case,
    get_branch_profile_with_permission_use_case,
    get_clinic_admin_use_case,
)
from app.api.main import app
from app.core.security import create_access_token
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


class FakeClinicAdminUseCase:
    async def list_clinics(self, user_id, skip=0, limit=100, status=None, search=None):
        return {
            "items": [
                {
                    "id": 1,
                    "name": "Clinica Central",
                    "description": "Clinica principal",
                    "address": "Main Street 123",
                    "city": "Ciudad",
                    "state": "Estado",
                    "country": "Pais",
                    "postal_code": "12345",
                    "phone": "555-0101",
                    "email": "clinic@example.com",
                    "lat": None,
                    "lng": None,
                    "is_active": True,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }
            ],
            "pagination": {"skip": skip, "limit": limit, "total": 1},
        }

    async def get_clinic(self, clinic_id, user_id):
        if clinic_id == 404:
            raise ValueError(f"Clinic with id {clinic_id} not found")
        return {
            "id": clinic_id,
            "name": "Clinica Central",
            "description": None,
            "address": "Main Street 123",
            "city": "Ciudad",
            "state": "Estado",
            "country": "Pais",
            "postal_code": "12345",
            "phone": None,
            "email": "clinic@example.com",
            "lat": None,
            "lng": None,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

    async def create_clinic(self, data, user_id):
        return {
            "id": 1,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            **data,
        }

    async def update_clinic(self, clinic_id, data, user_id):
        return await self.get_clinic(clinic_id, user_id) | data

    async def deactivate_clinic(self, clinic_id, user_id):
        return None


class FakeBranchAdminUseCase:
    async def list_branches(
        self, user_id, skip=0, limit=100, clinic_id=None, status=None
    ):
        return {
            "items": [
                {
                    "id": 1,
                    "clinic_id": clinic_id or 1,
                    "name": "Sucursal Centro",
                    "address": "Main Street 123",
                    "city": "Ciudad",
                    "state": "Estado",
                    "country": "Pais",
                    "postal_code": "12345",
                    "phone": None,
                    "email": "branch@example.com",
                    "lat": None,
                    "lng": None,
                    "is_active": True,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z",
                }
            ],
            "pagination": {"skip": skip, "limit": limit, "total": 1},
        }

    async def get_branch(self, branch_id, user_id):
        return {
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
            "lat": None,
            "lng": None,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

    async def create_branch(self, data, user_id):
        return {
            "id": 1,
            "is_active": True,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            **data,
        }

    async def update_branch(self, branch_id, data, user_id):
        return await self.get_branch(branch_id, user_id) | data

    async def deactivate_branch(self, branch_id, user_id):
        return None


class FakeBranchHoursAdminUseCase:
    async def list_hours(self, branch_id, user_id):
        return [
            {
                "id": 1,
                "branch_id": branch_id,
                "day_of_week": 1,
                "open_time": "09:00",
                "close_time": "18:00",
                "is_closed": False,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        ]

    async def create_hour(self, branch_id, data, user_id):
        return {
            "id": 1,
            "branch_id": branch_id,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            **data,
        }

    async def update_hour(self, branch_id, hour_id, data, user_id):
        return {
            "id": hour_id,
            "branch_id": branch_id,
            "day_of_week": 1,
            "open_time": "10:00",
            "close_time": "18:00",
            "is_closed": False,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            **data,
        }

    async def delete_hour(self, branch_id, hour_id, user_id):
        return None


@pytest.fixture(autouse=True)
def override_branch_use_cases():
    app.dependency_overrides[get_branch_profile_use_case] = (
        lambda: FakePublicBranchProfileUseCase()
    )
    app.dependency_overrides[get_branch_profile_with_permission_use_case] = (
        lambda: FakeProtectedBranchProfileUseCase()
    )
    app.dependency_overrides[get_clinic_admin_use_case] = (
        lambda: FakeClinicAdminUseCase()
    )
    app.dependency_overrides[get_branch_admin_use_case] = (
        lambda: FakeBranchAdminUseCase()
    )
    app.dependency_overrides[get_branch_hours_admin_use_case] = (
        lambda: FakeBranchHoursAdminUseCase()
    )
    yield
    app.dependency_overrides.pop(get_branch_profile_use_case, None)
    app.dependency_overrides.pop(get_branch_profile_with_permission_use_case, None)
    app.dependency_overrides.pop(get_clinic_admin_use_case, None)
    app.dependency_overrides.pop(get_branch_admin_use_case, None)
    app.dependency_overrides.pop(get_branch_hours_admin_use_case, None)


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


@pytest.mark.asyncio
async def test_list_clinics_requires_auth():
    """Clinic administration endpoints should require authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/clinics")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_clinics_returns_paginated_payload():
    """Clinic administration list should return a paginated payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/clinics",
            headers={"Authorization": "Bearer 1"},
            params={"skip": 0, "limit": 10, "status": "active"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["name"] == "Clinica Central"
    assert payload["pagination"] == {"skip": 0, "limit": 10, "total": 1}


@pytest.mark.asyncio
async def test_list_clinics_accepts_jwt_bearer_token():
    """Clinic administration list should also accept JWT bearer tokens."""
    token = create_access_token({"sub": "1"})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/clinics",
            headers={"Authorization": f"Bearer {token}"},
            params={"skip": 0, "limit": 10},
        )

    assert response.status_code == 200
    assert response.json()["pagination"] == {"skip": 0, "limit": 10, "total": 1}


@pytest.mark.asyncio
async def test_create_clinic_returns_created_clinic():
    """Clinic creation should return the created resource."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/clinics",
            headers={"Authorization": "Bearer 1"},
            json={
                "name": "Clinica Central",
                "address": "Main Street 123",
                "city": "Ciudad",
                "state": "Estado",
                "country": "Pais",
                "postal_code": "12345",
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Clinica Central"


@pytest.mark.asyncio
async def test_get_missing_clinic_returns_404():
    """Missing clinics should return a safe 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/clinics/404",
            headers={"Authorization": "Bearer 1"},
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_branches_returns_paginated_payload():
    """Branch administration list should return a paginated payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/branches",
            headers={"Authorization": "Bearer 1"},
            params={"clinic_id": 1, "limit": 10},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["clinic_id"] == 1
    assert payload["pagination"]["total"] == 1


@pytest.mark.asyncio
async def test_branch_hours_crud_contract():
    """Branch hours endpoints should expose create/list/update/delete contracts."""
    transport = ASGITransport(app=app)
    headers = {"Authorization": "Bearer 1"}
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        created = await ac.post(
            "/api/v1/branches/1/hours",
            headers=headers,
            json={
                "day_of_week": 1,
                "open_time": "09:00",
                "close_time": "18:00",
                "is_closed": False,
            },
        )
        listed = await ac.get("/api/v1/branches/1/hours", headers=headers)
        updated = await ac.put(
            "/api/v1/branches/1/hours/1",
            headers=headers,
            json={"open_time": "10:00"},
        )
        deleted = await ac.delete("/api/v1/branches/1/hours/1", headers=headers)

    assert created.status_code == 201
    assert listed.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["open_time"] == "10:00"
    assert deleted.status_code == 204


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
