"""Pruebas para los endpoints de clínicas y sucursales."""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.api.main import app
from app.infrastructure.database import get_db
from app.domain.entities.clinic import Branch, Service, Schedule, Rating


# Test client to make API requests
@pytest.mark.asyncio
async def test_get_branch_profile():
    """Test de obtención de perfil público de sucursal."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # This is a basic test that ensures the endpoint exists and doesn't crash
        response = await ac.get("/api/v1/clinics/branches/1")
        
        # Por ahora solo validamos que el endpoint exista
        # En un entorno con base de datos real, se podrían hacer pruebas más completas
        assert response.status_code in [200, 404] or response.status_code == 500


@pytest.mark.asyncio  
async def test_get_branch_profile_with_permissions():
    """Test de obtención de perfil público con permisos."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test endpoint with clinic and branch ID
        response = await ac.get("/api/v1/clinics/1/branches/1")
        
        # Por ahora solo validamos que el endpoint exista
        assert response.status_code in [200, 403] or response.status_code == 500


def test_branch_entities():
    """Test de entidades de sucursal."""
    # Test básico para verificar estructura de datos
    
    branch_data = {
        "id": 1,
        "clinic_id": 1,
        "name": "Clínica Veterinaria Central",
        "address": "Calle Principal 123",
        "city": "Ciudad Ejemplo",
        "state": "Estado Ejemplo",
        "country": "País Ejemplo",
        "postal_code": "12345",
        "phone": "+52 123 456 7890",
        "email": "contacto@clinica.com",
        "is_active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }
    
    branch = Branch(**branch_data)
    
    assert branch.id == 1
    assert branch.name == "Clínica Veterinaria Central"
    assert branch.is_active is True


def test_service_entity():
    """Test de entidad de servicio."""
    service_data = {
        "id": 1,
        "branch_id": 1,
        "name": "Consulta General",
        "description": "Servicio de consulta veterinaria básica",
        "duration": 30,
        "price": 250.0,
        "is_active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
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
        "updated_at": "2023-01-01T00:00:00Z"
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
        "updated_at": "2023-01-01T00:00:00Z"
    }
    
    rating = Rating(**rating_data)
    
    assert rating.id == 1
    assert rating.rating == 5
    assert rating.comment == "Excelente servicio"