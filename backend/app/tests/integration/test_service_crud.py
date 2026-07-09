"""
Test de CRUD para servicios
"""
import pytest
from sqlalchemy.orm import Session

from app.domain.entities.service import ServiceCreate, ServiceUpdate
from app.infrastructure.database.repositories.service_repository_impl import ServiceRepositoryImpl


def test_create_service(db_session: Session):
    """Prueba la creación de un servicio"""
    # Create repository instance  
    repo = ServiceRepositoryImpl(db_session)
    
    # Create service data
    service_data = ServiceCreate(
        branch_id=1,
        name="Servicio de Vacunación",
        description="Vacunación completa para mascotas",
        duration=60,
        price=250.0,
        is_active=True
    )
    
    # Create service
    service = repo.create_service(service_data)
    
    # Verify creation
    assert service.id is not None
    assert service.name == "Servicio de Vacunación"
    assert service.branch_id == 1
    assert service.duration == 60
    assert service.price == 250.0
    assert service.is_active is True


def test_get_service(db_session: Session):
    """Prueba la obtención de un servicio por ID"""
    # Create repository instance  
    repo = ServiceRepositoryImpl(db_session)
    
    # Try to get a service that doesn't exist
    service = repo.get_service(99999)
    assert service is None
    
    # Create and get an existing service 
    service_data = ServiceCreate(
        branch_id=1,
        name="Servicio de Consulta",
        description="Consulta veterinaria mensual",
        duration=30,
        price=150.0,
        is_active=True
    )
    
    created_service = repo.create_service(service_data)
    retrieved_service = repo.get_service(created_service.id)
    
    assert retrieved_service is not None
    assert retrieved_service.name == "Servicio de Consulta"
    assert retrieved_service.id == created_service.id


def test_update_service(db_session: Session):
    """Prueba la actualización de un servicio"""
    # Create repository instance  
    repo = ServiceRepositoryImpl(db_session)
    
    # Create a service
    service_data = ServiceCreate(
        branch_id=1,
        name="Servicio de Limpieza",
        description="Limpieza y cuidado de pelaje",
        duration=45,
        price=200.0,
        is_active=True
    )
    
    created_service = repo.create_service(service_data)
    
    # Update the service
    update_data = ServiceUpdate(
        name="Servicio de Limpieza y Paseo",
        description="Limpieza, cuidado de pelaje y paseo",
        duration=60,
        price=250.0,
        is_active=False
    )
    
    updated_service = repo.update_service(created_service.id, update_data)
    
    # Verify update
    assert updated_service is not None
    assert updated_service.name == "Servicio de Limpieza y Paseo"
    assert updated_service.description == "Limpieza, cuidado de pelaje y paseo"
    assert updated_service.duration == 60
    assert updated_service.price == 250.0
    assert updated_service.is_active is False


def test_delete_service(db_session: Session):
    """Prueba la eliminación de un servicio"""
    # Create repository instance  
    repo = ServiceRepositoryImpl(db_session)
    
    # Create a service
    service_data = ServiceCreate(
        branch_id=1,
        name="Servicio de Corte",
        description="Corte de pelo y uñas",
        duration=45,
        price=180.0,
        is_active=True
    )
    
    created_service = repo.create_service(service_data)
    
    # Delete the service
    success = repo.delete_service(created_service.id)
    
    # Verify deletion
    assert success is True
    
    # Try to get the deleted service 
    deleted_service = repo.get_service(created_service.id)
    assert deleted_service is None


def test_get_services_by_branch(db_session: Session):
    """Prueba la obtención de servicios por sucursal"""
    # Create repository instance  
    repo = ServiceRepositoryImpl(db_session)
    
    # Create multiple services for same branch
    service_data_1 = ServiceCreate(
        branch_id=1,
        name="Servicio 1",
        description="Descripción 1",
        duration=30,
        price=100.0,
        is_active=True
    )
    
    service_data_2 = ServiceCreate(
        branch_id=1,
        name="Servicio 2",
        description="Descripción 2",
        duration=45,
        price=150.0,
        is_active=True
    )
    
    # Create services in DB
    repo.create_service(service_data_1)
    repo.create_service(service_data_2)
    
    # Get services for branch
    services = repo.get_services(1, skip=0, limit=100)
    
    # Verify result
    assert len(services) >= 2
    branch_ids = [s.branch_id for s in services]
    assert all(bid == 1 for bid in branch_ids)