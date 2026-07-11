"""
Test de endpoints API para veterinarios
"""
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_veterinarian():
    """Prueba crear un veterinario a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/veterinarians/",
            json={
                "branch_id": 1,
                "name": "Carlos",
                "last_name": "García",
                "specialty": "Cirugía",
                "email": "carlos.garcia@example.com",
                "phone": "555-0123",
                "license_number": "LIC12345",
                "is_active": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Carlos"
        assert data["branch_id"] == 1


@pytest.mark.asyncio
async def test_get_veterinarian():
    """Prueba obtener un veterinario a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a veterinarian
        create_response = await client.post(
            "/api/v1/veterinarians/",
            json={
                "branch_id": 1,
                "name": "María",
                "last_name": "Rodríguez",
                "specialty": "Medicina General",
                "email": "maria.rodriguez@example.com",
                "phone": "555-0456",
                "license_number": "LIC67890",
                "is_active": True,
            },
        )

        assert create_response.status_code == 201
        created_vet = create_response.json()
        vet_id = created_vet["id"]

        # Then get it
        get_response = await client.get(f"/api/v1/veterinarians/{vet_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["name"] == "María"
        assert data["id"] == vet_id


@pytest.mark.asyncio
async def test_get_veterinarians_by_branch():
    """Prueba obtener veterinarios por sucursal"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/veterinarians/?branch_id=1")

        assert response.status_code == 200
        data = response.json()
        # This could return empty list or some existing veterinarians
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_update_veterinarian():
    """Prueba actualizar un veterinario a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a veterinarian
        create_response = await client.post(
            "/api/v1/veterinarians/",
            json={
                "branch_id": 1,
                "name": "Juan",
                "last_name": "Pérez",
                "specialty": "Medicina Familiar",
                "email": "juan.perez@example.com",
                "phone": "555-0789",
                "license_number": "LIC11111",
                "is_active": True,
            },
        )

        assert create_response.status_code == 201
        created_vet = create_response.json()
        vet_id = created_vet["id"]

        # Then update it
        update_response = await client.put(
            f"/api/v1/veterinarians/{vet_id}",
            json={
                "name": "Juan Carlos",
                "last_name": "Pérez",
                "specialty": "Pediatría Veterinaria",
                "email": "juan.c.perez@example.com",
                "phone": "555-0789",
                "license_number": "LIC11112",
                "is_active": False,
            },
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Juan Carlos"
        assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_veterinarian():
    """Prueba eliminar un veterinario a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a veterinarian
        create_response = await client.post(
            "/api/v1/veterinarians/",
            json={
                "branch_id": 1,
                "name": "Ana",
                "last_name": "Martínez",
                "specialty": "Nutrición",
                "email": "ana.martinez@example.com",
                "phone": "555-0987",
                "license_number": "LIC22222",
                "is_active": True,
            },
        )

        assert create_response.status_code == 201
        created_vet = create_response.json()
        vet_id = created_vet["id"]

        # Then delete it
        delete_response = await client.delete(f"/api/v1/veterinarians/{vet_id}")

        assert delete_response.status_code == 204
