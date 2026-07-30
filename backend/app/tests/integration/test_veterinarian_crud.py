"""
Test de CRUD para veterinarios
"""

from sqlalchemy.orm import Session

from app.domain.entities.veterinarian import VeterinarianCreate, VeterinarianUpdate
from app.infrastructure.database.repositories.veterinarian_repository_impl import (
    VeterinarianRepositoryImpl,
)


def test_create_veterinarian(db_session: Session):
    """Prueba la creación de un veterinario"""
    # Create repository instance
    repo = VeterinarianRepositoryImpl(db_session)

    # Create veterinarian data
    vet_data = VeterinarianCreate(
        branch_id=1,
        name="Carlos",
        last_name="García",
        specialty="Cirugía",
        email="carlos.garcia@example.com",
        phone="555-0123",
        license_number="LIC12345",
        is_active=True,
    )

    # Create veterinarian
    veterinarian = repo.create_veterinarian(vet_data)

    # Verify creation
    assert veterinarian.id is not None
    assert veterinarian.name == "Carlos"
    assert veterinarian.last_name == "García"
    assert veterinarian.branch_id == 1
    assert veterinarian.specialty == "Cirugía"
    assert veterinarian.email == "carlos.garcia@example.com"
    assert veterinarian.license_number == "LIC12345"
    assert veterinarian.is_active is True


def test_get_veterinarian(db_session: Session):
    """Prueba la obtención de un veterinario por ID"""
    # Create repository instance
    repo = VeterinarianRepositoryImpl(db_session)

    # Try to get a veterinarian that doesn't exist
    veterinarian = repo.get_veterinarian(99999)
    assert veterinarian is None

    # Create and get an existing veterinarian
    vet_data = VeterinarianCreate(
        branch_id=1,
        name="María",
        last_name="Rodríguez",
        specialty="Medicina General",
        email="maria.rodriguez@example.com",
        phone="555-0456",
        license_number="LIC67890",
        is_active=True,
    )

    created_veterinarian = repo.create_veterinarian(vet_data)
    retrieved_veterinarian = repo.get_veterinarian(created_veterinarian.id)

    assert retrieved_veterinarian is not None
    assert retrieved_veterinarian.name == "María"
    assert retrieved_veterinarian.id == created_veterinarian.id


def test_update_veterinarian(db_session: Session):
    """Prueba la actualización de un veterinario"""
    # Create repository instance
    repo = VeterinarianRepositoryImpl(db_session)

    # Create a veterinarian
    vet_data = VeterinarianCreate(
        branch_id=1,
        name="Juan",
        last_name="Pérez",
        specialty="Medicina Familiar",
        email="juan.perez@example.com",
        phone="555-0789",
        license_number="LIC11111",
        is_active=True,
    )

    created_veterinarian = repo.create_veterinarian(vet_data)

    # Update the veterinarian
    update_data = VeterinarianUpdate(
        name="Juan Carlos",
        last_name="Pérez",
        specialty="Pediatría Veterinaria",
        email="juan.c.perez@example.com",
        phone="555-0789",
        license_number="LIC11112",
        is_active=False,
    )

    updated_veterinarian = repo.update_veterinarian(
        created_veterinarian.id, update_data
    )

    # Verify update
    assert updated_veterinarian is not None
    assert updated_veterinarian.name == "Juan Carlos"
    assert updated_veterinarian.last_name == "Pérez"
    assert updated_veterinarian.specialty == "Pediatría Veterinaria"
    assert updated_veterinarian.email == "juan.c.perez@example.com"
    assert updated_veterinarian.license_number == "LIC11112"
    assert updated_veterinarian.is_active is False


def test_delete_veterinarian(db_session: Session):
    """Prueba la eliminación de un veterinario"""
    # Create repository instance
    repo = VeterinarianRepositoryImpl(db_session)

    # Create a veterinarian
    vet_data = VeterinarianCreate(
        branch_id=1,
        name="Ana",
        last_name="Martínez",
        specialty="Nutrición",
        email="ana.martinez@example.com",
        phone="555-0987",
        license_number="LIC22222",
        is_active=True,
    )

    created_veterinarian = repo.create_veterinarian(vet_data)

    # Delete the veterinarian
    success = repo.delete_veterinarian(created_veterinarian.id)

    # Verify deletion
    assert success is True

    # Try to get the deleted veterinarian
    deleted_veterinarian = repo.get_veterinarian(created_veterinarian.id)
    assert deleted_veterinarian is None


def test_get_veterinarians_by_branch(db_session: Session):
    """Prueba la obtención de veterinarios por sucursal"""
    # Create repository instance
    repo = VeterinarianRepositoryImpl(db_session)

    # Create multiple veterinarians for same branch
    vet_data_1 = VeterinarianCreate(
        branch_id=1,
        name="Veterinario 1",
        last_name="Apellido1",
        specialty="Especialidad 1",
        email="vet1@example.com",
        phone="555-0101",
        license_number="LIC33333",
        is_active=True,
    )

    vet_data_2 = VeterinarianCreate(
        branch_id=1,
        name="Veterinario 2",
        last_name="Apellido2",
        specialty="Especialidad 2",
        email="vet2@example.com",
        phone="555-0202",
        license_number="LIC44444",
        is_active=True,
    )

    # Create veterinarians in DB
    repo.create_veterinarian(vet_data_1)
    repo.create_veterinarian(vet_data_2)

    # Get veterinarians for branch
    veterinarians = repo.get_veterinarians(1, skip=0, limit=100)

    # Verify result
    assert len(veterinarians) >= 2
    branch_ids = [v.branch_id for v in veterinarians]
    assert all(bid == 1 for bid in branch_ids)
