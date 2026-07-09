"""
Test de endpoints API para usuarios internos
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.infrastructure.database.session import get_db
from app.tests.integration.test_internal_user_crud import InternalUserRepositoryImpl
from app.domain.entities.internal_user import InternalUserCreate


@pytest.mark.asyncio
async def test_create_internal_user():
    """Prueba crear un usuario interno a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/internal-users/", json={
            "branch_id": 1,
            "name": "Carlos",
            "last_name": "Gómez",
            "email": "carlos.gomez@example.com",
            "role": "admin",
            "password": "password123",
            "is_active": True
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Carlos"
        assert data["branch_id"] == 1


@pytest.mark.asyncio 
async def test_get_internal_user():
    """Prueba obtener un usuario interno a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create an internal user
        create_response = await client.post("/api/v1/internal-users/", json={
            "branch_id": 1,
            "name": "María",
            "last_name": "López",
            "email": "maria.lopez@example.com",
            "role": "editor",
            "password": "password456",
            "is_active": True
        })
        
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # Then get it 
        get_response = await client.get(f"/api/v1/internal-users/{user_id}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["name"] == "María"
        assert data["id"] == user_id


@pytest.mark.asyncio
async def test_get_internal_users_by_branch():
    """Prueba obtener usuarios internos por sucursal"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/internal-users/?branch_id=1")
        
        assert response.status_code == 200
        data = response.json()
        # This could return empty list or some existing users
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_update_internal_user():
    """Prueba actualizar un usuario interno a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create an internal user
        create_response = await client.post("/api/v1/internal-users/", json={
            "branch_id": 1,
            "name": "Pedro",
            "last_name": "Sánchez",
            "email": "pedro.sanchez@example.com",
            "role": "editor",
            "password": "password789",
            "is_active": True
        })
        
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # Then update it
        update_response = await client.put(f"/api/v1/internal-users/{user_id}", json={
            "name": "Pedro Miguel",
            "last_name": "Sánchez",
            "email": "pedro.m.sanchez@example.com",
            "role": "admin",
            "password": "newpassword123",
            "is_active": False
        })
        
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Pedro Miguel"
        assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_internal_user():
    """Prueba eliminar un usuario interno a través de la API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First create an internal user
        create_response = await client.post("/api/v1/internal-users/", json={
            "branch_id": 1,
            "name": "Ana",
            "last_name": "Fernández",
            "email": "ana.fernandez@example.com",
            "role": "editor",
            "password": "password321",
            "is_active": True
        })
        
        assert create_response.status_code == 201
        created_user = create_response.json()
        user_id = created_user["id"]
        
        # Then delete it
        delete_response = await client.delete(f"/api/v1/internal-users/{user_id}")
        
        assert delete_response.status_code == 204
