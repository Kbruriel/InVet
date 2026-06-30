"""Pruebas unitarias para casos de uso de clínicas."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.clinic_use_case import GetBranchProfileUseCase


@pytest.fixture
def mock_branch_repo():
    """Crea un repositorio de sucursal simulado."""
    repo = AsyncMock()
    repo.get_branch_by_id.return_value = MagicMock(
        id=1,
        clinic_id=1,
        name="Clínica Veterinaria Central",
        address="Calle Principal 123",
        city="Ciudad Ejemplo",
        state="Estado Ejemplo", 
        country="País Ejemplo",
        postal_code="12345",
        phone="+52 123 456 7890",
        email="contacto@clinica.com",
        is_active=True,
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z"
    )
    return repo


@pytest.fixture
def mock_service_repo():
    """Crea un repositorio de servicios simulado."""
    repo = AsyncMock()
    repo.list_active_services_by_branch.return_value = []
    return repo


@pytest.fixture
def mock_schedule_repo():
    """Crea un repositorio de horarios simulado."""
    repo = AsyncMock()
    repo.list_schedule_by_branch.return_value = []
    return repo


@pytest.fixture
def mock_rating_repo():
    """Crea un repositorio de calificaciones simulado."""
    repo = AsyncMock()
    repo.get_ratings_summary_by_branch.return_value = {
        "average_rating": 0.0,
        "total_ratings": 0,
        "rating_distribution": {}
    }
    return repo


@pytest.mark.asyncio
async def test_get_branch_profile_use_case(
    mock_branch_repo, 
    mock_service_repo, 
    mock_schedule_repo, 
    mock_rating_repo
):
    """Test del caso de uso para obtener perfil de sucursal."""
    
    # Crear el caso de uso con los repositorios simulados
    use_case = GetBranchProfileUseCase(
        branch_repo=mock_branch_repo,
        service_repo=mock_service_repo,
        schedule_repo=mock_schedule_repo,
        rating_repo=mock_rating_repo
    )
    
    # Ejecutar el caso de uso
    result = await use_case.execute(1)
    
    # Validar que se devolvió una respuesta
    assert "branch" in result
    assert "services" in result
    assert "schedules" in result
    assert "ratings_summary" in result
    
    # Validar datos de la sucursal
    assert result["branch"]["id"] == 1
    assert result["branch"]["name"] == "Clínica Veterinaria Central"


@pytest.mark.asyncio
async def test_get_branch_profile_use_case_with_not_found(
    mock_branch_repo, 
    mock_service_repo,
    mock_schedule_repo,
    mock_rating_repo  
):
    """Test de caso de uso cuando no se encuentra la sucursal."""
    
    # Configurar el repositorio para que devuelva None
    mock_branch_repo.get_branch_by_id.return_value = None
    
    use_case = GetBranchProfileUseCase(
        branch_repo=mock_branch_repo,
        service_repo=mock_service_repo,
        schedule_repo=mock_schedule_repo,
        rating_repo=mock_rating_repo
    )
    
    # Verificar que se lanza una excepción
    with pytest.raises(ValueError):
        await use_case.execute(999)