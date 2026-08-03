import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.domain.user import UserCreate, UserRole
from app.domain.value_objects import AuthCredentials
from app.application.auth_use_cases import AuthUseCase
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.session_repository import SessionRepository

def test_register_user_success():
    """Test para registro exitoso de usuario"""
    # Mock de repositorios
    mock_user_repo = Mock()
    mock_session_repo = Mock()
    
    # Configurar el mock para evitar duplicados
    mock_user_repo.get_by_email.return_value = None
    
    # Datos de prueba
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    
    # Objeto de usuario devuelto por el repositorio (simulación)
    returned_user = Mock()
    returned_user.id = 1
    returned_user.email = "test@example.com"
    returned_user.first_name = "Test"
    returned_user.last_name = "User"
    returned_user.role = UserRole.CLIENT
    returned_user.is_active = True
    returned_user.created_at = datetime.utcnow()
    returned_user.updated_at = datetime.utcnow()
    
    mock_user_repo.create_user.return_value = returned_user
    
    # Crear use case
    auth_use_case = AuthUseCase(mock_user_repo, mock_session_repo)
    
    # Ejecutar registro
    result = auth_use_case.register_user(user_data)
    
    # Verificaciones
    assert result.email == user_data.email
    assert result.first_name == user_data.first_name
    assert result.last_name == user_data.last_name
    mock_user_repo.create_user.assert_called_once()

def test_register_user_duplicate_email():
    """Test para registro con email duplicado"""
    # Mock de repositorios
    mock_user_repo = Mock()
    mock_session_repo = Mock()
    
    # Configurar el mock para devolver un usuario existente (duplicado)
    mock_user_repo.get_by_email.return_value = Mock()
    
    # Datos de prueba
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    
    # Crear use case
    auth_use_case = AuthUseCase(mock_user_repo, mock_session_repo)
    
    # Ejecutar registro - debería lanzar excepción
    with pytest.raises(Exception) as exc_info:
        auth_use_case.register_user(user_data)
    
    assert "already registered" in str(exc_info.value)

def test_authenticate_user_success():
    """Test para autenticación exitosa"""
    # Mock de repositorios
    mock_user_repo = Mock()
    mock_session_repo = Mock()
    
    # Configurar el mock para devolver un usuario
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.hashed_password = "hashed_password_123"
    user.is_active = True
    user.role = UserRole.CLIENT
    
    mock_user_repo.get_by_email.return_value = user
    
    # Datos de credenciales de prueba
    credentials = AuthCredentials(
        email="test@example.com",
        password="password123"
    )
    
    # Crear use case
    auth_use_case = AuthUseCase(mock_user_repo, mock_session_repo)
    
    # Ejecutar autenticación con mock de verify_password
    with patch('app.core.security.verify_password') as mock_verify:
        mock_verify.return_value = True  # Contraseña correcta
        
        # Ejecutar el método real de autenticación (con mocks parciales)
        result = auth_use_case.authenticate_user(credentials)
        
        # Verificación general
        assert result is not None

def test_authenticate_user_invalid_credentials():
    """Test para autenticación con credenciales inválidas"""
    # Mock de repositorios
    mock_user_repo = Mock()
    mock_session_repo = Mock()
    
    # Configurar el mock para no devolver usuario
    mock_user_repo.get_by_email.return_value = None
    
    # Datos de credenciales de prueba
    credentials = AuthCredentials(
        email="test@example.com",
        password="password123"
    )
    
    # Crear use case
    auth_use_case = AuthUseCase(mock_user_repo, mock_session_repo)
    
    # Ejecutar autenticación - debería lanzar excepción
    with pytest.raises(Exception) as exc_info:
        auth_use_case.authenticate_user(credentials)
    
    assert "Invalid credentials" in str(exc_info.value)

def test_authenticate_user_inactive_user():
    """Test para autenticación de usuario inactivo"""
    # Mock de repositorios
    mock_user_repo = Mock()
    mock_session_repo = Mock()
    
    # Configurar el mock para devolver un usuario inactivo
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.hashed_password = "hashed_password_123"
    user.is_active = False  # Usuario inactivo
    
    mock_user_repo.get_by_email.return_value = user
    
    # Datos de credenciales de prueba
    credentials = AuthCredentials(
        email="test@example.com",
        password="password123"
    )
    
    # Crear use case
    auth_use_case = AuthUseCase(mock_user_repo, mock_session_repo)
    
    # Ejecutar autenticación - debería lanzar excepción
    with pytest.raises(Exception) as exc_info:
        auth_use_case.authenticate_user(credentials)
    
    assert "not active" in str(exc_info.value)