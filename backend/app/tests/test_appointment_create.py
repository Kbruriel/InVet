"""Tests para el endpoint de creación de citas (POST /appointments)."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.app import app
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.models.user import User as UserModel
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.pet import Pet as PetModel
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.appointment import Appointment as AppointmentModel


# URL de prueba: base en memoria para evitar dependencia de BD externa
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    """Cliente de prueba con base en memoria."""
    from app.infrastructure.database.base import Base
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


@pytest.fixture
def db_session():
    """Sesión de BD limpia para cada test."""
    from app.infrastructure.database.base import Base
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def authenticated_user(db_session):
    """Usuario autenticado (propietario de una clínica)."""
    from app.infrastructure.database.models.user import UserRole
    user = UserModel(
        email="owner@test.com",
        password="hashed_password",
        full_name="Test Owner",
        role=UserRole.OWNER,
        clinic_id=1,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_clinic(db_session):
    """Clínica de prueba."""
    clinic = ClinicModel(name="Clínica Test", address="Dirección Test")
    db_session.add(clinic)
    db_session.commit()
    db_session.refresh(clinic)
    return clinic


@pytest.fixture
def test_owner(db_session, test_clinic):
    """Propietario de prueba vinculado a la clínica."""
    owner = OwnerModel(user_id=1, clinic_id=test_clinic.id, phone="1234567890")
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    return owner


@pytest.fixture
def test_pet(db_session, test_owner):
    """Mascota de prueba."""
    pet = PetModel(owner_id=test_owner.id, name="Max", species="perro")
    db_session.add(pet)
    db_session.commit()
    db_session.refresh(pet)
    return pet


def test_create_appointment_success(client, authenticated_user, test_clinic, test_owner, test_pet):
    """AC-008-03: Crear una cita exitosamente."""
    with patch('app.api.v1.dependencies.get_current_access_user', return_value=MagicMock(
        id=authenticated_user.id,
        clinic_id=test_clinic.id,
        role=UserRole.OWNER,
        is_active=True,
    )):
        response = client.post("/api/v1/appointments", json={
            "owner_id": test_owner.id,
            "pet_id": test_pet.id,
            "veterinarian_id": None,
            "scheduled_start": "2026-12-31T10:00:00",
            "scheduled_end": "2026-12-31T10:30:00",
            "reason": "Consulta general",
        })
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["status"] == "pending"
    assert data["appointment_type"] == "consultation"
    assert data["reason"] == "Consulta general"


def test_create_appointment_with_veterinarian(client, authenticated_user, test_clinic, test_owner, test_pet):
    """AC-008-04: Crear una cita con veterinario asignado."""
    from app.infrastructure.database.models.user import UserRole as UR
    
    # Crear un veterinario de prueba
    vet = UserModel(
        email="vet@test.com",
        password="hashed_password",
        full_name="Dr. Test",
        role=UR.VETERINARIAN,
        clinic_id=test_clinic.id,
        is_active=True,
    )
    with patch('app.api.v1.dependencies.get_current_access_user', return_value=MagicMock(
        id=authenticated_user.id,
        clinic_id=test_clinic.id,
        role=UR.OWNER,
        is_active=True,
    )):
        response = client.post("/api/v1/appointments", json={
            "owner_id": test_owner.id,
            "pet_id": test_pet.id,
            "veterinarian_id": vet.id,
            "scheduled_start": "2026-12-31T14:00:00",
            "scheduled_end": "2026-12-31T14:45:00",
            "reason": "Vacunación",
            "appointment_type": "vaccination",
        })
    
    assert response.status_code == 201
    data = response.json()
    assert data["veterinarian_id"] == vet.id


def test_create_appointment_past_date(client, authenticated_user):
    """AC-008-05 (negativo): No permitir citas en el pasado."""
    from app.infrastructure.database.models.user import UserRole
    
    with patch('app.api.v1.dependencies.get_current_access_user', return_value=MagicMock(
        id=authenticated_user.id,
        clinic_id=1,
        role=UserRole.OWNER,
        is_active=True,
    )):
        response = client.post("/api/v1/appointments", json={
            "owner_id": 1,
            "pet_id": None,
            "scheduled_start": "2020-01-01T10:00:00",
            "scheduled_end": "2020-01-01T10:30:00",
            "reason": "Test",
        })
    
    assert response.status_code == 422


def test_create_appointment_invalid_duration(client, authenticated_user):
    """AC-008-06 (negativo): Validar duración mínima de 15 minutos."""
    from app.infrastructure.database.models.user import UserRole
    
    with patch('app.api.v1.dependencies.get_current_access_user', return_value=MagicMock(
        id=authenticated_user.id,
        clinic_id=1,
        role=UserRole.OWNER,
        is_active=True,
    )):
        response = client.post("/api/v1/appointments", json={
            "owner_id": 1,
            "pet_id": None,
            "scheduled_start": "2026-12-31T10:00:00",
            "scheduled_end": "2026-12-31T10:10:00",  # Solo 10 minutos
            "reason": "Test",
        })
    
    assert response.status_code == 422


def test_create_appointment_unauthenticated(client):
    """AC-008-02 (negativo): Sin autenticación, debe rechazar."""
    response = client.post("/api/v1/appointments", json={
        "owner_id": 1,
        "scheduled_start": "2026-12-31T10:00:00",
        "scheduled_end": "2026-12-31T10:30:00",
    })
    
    assert response.status_code == 401
