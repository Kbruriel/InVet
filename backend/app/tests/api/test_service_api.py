"""
Test de endpoints API para servicios
"""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_service():
    """Prueba crear un servicio a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/services/",
            json={
                "branch_id": 1,
                "name": "Servicio de Vacunación",
                "description": "Vacunación completa para mascotas",
                "duration": 60,
                "price": 250.0,
                "is_active": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Servicio de Vacunación"
        assert data["branch_id"] == 1


@pytest.mark.asyncio
async def test_get_service():
    """Prueba obtener un servicio a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a service
        create_response = await client.post(
            "/api/v1/services/",
            json={
                "branch_id": 1,
                "name": "Servicio de Consulta",
                "description": "Consulta veterinaria mensual",
                "duration": 30,
                "price": 150.0,
                "is_active": True,
            },
        )

        assert create_response.status_code == 201
        created_service = create_response.json()
        service_id = created_service["id"]

        # Then get it
        get_response = await client.get(f"/api/v1/services/{service_id}")

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["name"] == "Servicio de Consulta"
        assert data["id"] == service_id


@pytest.mark.asyncio
async def test_get_services_by_branch():
    """Prueba obtener servicios por sucursal"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/services/?branch_id=1")

        assert response.status_code == 200
        data = response.json()
        # This could return empty list or some existing services
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_update_service():
    """Prueba actualizar un servicio a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a service
        create_response = await client.post(
            "/api/v1/services/",
            json={
                "branch_id": 1,
                "name": "Servicio de Limpieza",
                "description": "Limpieza y cuidado de pelaje",
                "duration": 45,
                "price": 200.0,
                "is_active": True,
            },
        )

        assert create_response.status_code == 201
        created_service = create_response.json()
        service_id = created_service["id"]

        # Then update it
        update_response = await client.put(
            f"/api/v1/services/{service_id}",
            json={
                "name": "Servicio de Limpieza y Paseo",
                "description": "Limpieza, cuidado de pelaje y paseo",
                "duration": 60,
                "price": 250.0,
                "is_active": False,
            },
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Servicio de Limpieza y Paseo"
        assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_service():
    """Prueba eliminar un servicio a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create a service
        create_response = await client.post(
            "/api/v1/services/",
            json={
                "branch_id": 1,
                "name": "Servicio de Corte",
                "description": "Corte de pelo y uñas",
                "duration": 45,
                "price": 180.0,
                "is_active": True,
            },
        )

        assert create_response.status_code == 201
        created_service = create_response.json()
        service_id = created_service["id"]

        # Then delete it
        delete_response = await client.delete(f"/api/v1/services/{service_id}")

        assert delete_response.status_code == 204
