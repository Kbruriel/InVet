"""
Test de CRUD para usuarios internos
"""
import pytest
from sqlalchemy.orm import Session

from app.domain.entities.internal_user import InternalUserCreate, InternalUserUpdate
from app.infrastructure.database.repositories.internal_user_repository_impl import InternalUserRepositoryImpl


def test_create_internal_user(db_session: Session):
    """Prueba la creación de un usuario interno"""
    # Create repository instance  
    repo = InternalUserRepositoryImpl(db_session)
    
    # Create user data
    user_data = InternalUserCreate(
        branch_id=1,
        name="Carlos",
        last_name="Gómez",
        email="carlos.gomez@example.com",
        role="admin",
        password="password123",  # This will be hashed in the repository
        is_active=True
    )
    
    # Create user
    user = repo.create_internal_user(user_data)
    
    # Verify creation
    assert user.id is not None
    assert user.name == "Carlos"
    assert user.last_name == "Gómez"
    assert user.branch_id == 1
    assert user.email == "carlos.gomez@example.com"
    assert user.role == "admin"
    assert user.is_active is True


def test_get_internal_user(db_session: Session):
    """Prueba la obtención de un usuario interno por ID"""
    # Create repository instance  
    repo = InternalUserRepositoryImpl(db_session)
    
    # Try to get a user that doesn't exist
    user = repo.get_internal_user(99999)
    assert user is None
    
    # Create and get an existing user 
    user_data = InternalUserCreate(
        branch_id=1,
        name="María",
        last_name="López",
        email="maria.lopez@example.com",
        role="editor",
        password="password456",
        is_active=True
    )
    
    created_user = repo.create_internal_user(user_data)
    retrieved_user = repo.get_internal_user(created_user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.name == "María"
    assert retrieved_user.id == created_user.id


def test_update_internal_user(db_session: Session):
    """Prueba la actualización de un usuario interno"""
    # Create repository instance  
    repo = InternalUserRepositoryImpl(db_session)
    
    # Create a user
    user_data = InternalUserCreate(
        branch_id=1,
        name="Pedro",
        last_name="Sánchez",
        email="pedro.sanchez@example.com",
        role="editor",
        password="password789",
        is_active=True
    )
    
    created_user = repo.create_internal_user(user_data)
    
    # Update the user
    update_data = InternalUserUpdate(
        name="Pedro Miguel",
        last_name="Sánchez",
        email="pedro.m.sanchez@example.com",
        role="admin",
        password="newpassword123",  # New password will be hashed
        is_active=False
    )
    
    updated_user = repo.update_internal_user(created_user.id, update_data)
    
    # Verify update
    assert updated_user is not None
    assert updated_user.name == "Pedro Miguel"
    assert updated_user.last_name == "Sánchez"
    assert updated_user.email == "pedro.m.sanchez@example.com"
    assert updated_user.role == "admin"
    assert updated_user.is_active is False


def test_delete_internal_user(db_session: Session):
    """Prueba la eliminación de un usuario interno"""
    # Create repository instance  
    repo = InternalUserRepositoryImpl(db_session)
    
    # Create a user
    user_data = InternalUserCreate(
        branch_id=1,
        name="Ana",
        last_name="Fernández",
        email="ana.fernandez@example.com",
        role="editor",
        password="password321",
        is_active=True
    )
    
    created_user = repo.create_internal_user(user_data)
    
    # Delete the user
    success = repo.delete_internal_user(created_user.id)
    
    # Verify deletion
    assert success is True
    
    # Try to get the deleted user 
    deleted_user = repo.get_internal_user(created_user.id)
    assert deleted_user is None


def test_get_internal_users_by_branch(db_session: Session):
    """Prueba la obtención de usuarios internos por sucursal"""
    # Create repository instance  
    repo = InternalUserRepositoryImpl(db_session)
    
    # Create multiple users for same branch
    user_data_1 = InternalUserCreate(
        branch_id=1,
        name="Usuario 1",
        last_name="Apellido1",
        email="user1@example.com",
        role="admin",
        password="password01",
        is_active=True
    )
    
    user_data_2 = InternalUserCreate(
        branch_id=1,
        name="Usuario 2",
        last_name="Apellido2",
        email="user2@example.com",
        role="editor",
        password="password02",
        is_active=True
    )
    
    # Create users in DB
    repo.create_internal_user(user_data_1)
    repo.create_internal_user(user_data_2)
    
    # Get users for branch
    users = repo.get_internal_users(1, skip=0, limit=100)
    
    # Verify result
    assert len(users) >= 2
    branch_ids = [u.branch_id for u in users]
    assert all(bid == 1 for bid in branch_ids)