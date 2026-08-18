"""Tests para el endpoint de creación de citas (POST /appointments)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.app import app
from app.domain.user import UserRole

# Sobrescribir el engine global de session.py con SQLite en memoria ANTES de importar la app
from app.infrastructure.database import session as session_module
from app.infrastructure.database.models.branch import Branch as BranchModel
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.pet import Pet as PetModel
from app.infrastructure.database.models.user import User as UserModel
from app.infrastructure.database.session import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
session_module.engine = test_engine
session_module.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)
TestingSessionLocal = session_module.SessionLocal


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


class _MockUser:
    """Mock user object with attribute access for auth override."""

    def __init__(self):
        self.id = 1
        self.user_id = 1
        self.email = "owner@test.com"
        self.username = "owner_test_001"
        self.role = UserRole.OWNER.value
        self.clinic_id = 1
        self.is_active = True


def override_auth():
    """Override auth dependency to return a dict (el router llama a .get())."""
    return {
        "id": 1,
        "user_id": 1,
        "email": "owner@test.com",
        "username": "owner_test_001",
        "role": UserRole.OWNER.value,
        "clinic_id": 1,
        "is_active": True,
    }


@pytest.fixture(scope="module")
def client():
    """Cliente de prueba con base en memoria."""
    from app.api.v1.routers.appointment_router import get_current_db as router_get_db
    from app.core.security import get_current_access_user as auth_dep

    # Override both db and auth for in-memory testing
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth_dep] = override_auth
    # Also override the router's local dependency reference
    app.dependency_overrides[router_get_db] = override_get_db

    Base.metadata.create_all(bind=test_engine)

    client = TestClient(app)
    client.test_user = _MockUser()
    return client


@pytest.fixture
def db_session():
    """Sesión de BD limpia para cada test."""
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def authenticated_user(db_session):
    """Usuario autenticado (propietario de una clínica)."""
    user = db_session.query(UserModel).filter_by(email="owner@test.com").first()
    if user:
        return user

    existing_username = db_session.query(UserModel).filter_by(username="owner").first()
    if existing_username:
        return existing_username

    user = UserModel(
        email="owner@test.com",
        username=f"owner_test_{uuid.uuid4().hex}",
        hashed_password="hashed_password",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_clinic(db_session):
    """Clínica de prueba."""
    clinic = db_session.query(ClinicModel).filter_by(name="Clínica Test").first()
    if clinic:
        return clinic

    clinic = ClinicModel(
        name="Clínica Test",
        address="Dirección Test",
        city="Ciudad Test",
        state="Estado Test",
        country="País Test",
        postal_code="000003",
    )
    db_session.add(clinic)
    db_session.flush()
    return clinic


@pytest.fixture
def test_branch(db_session, test_clinic):
    """Sucursal de prueba vinculada a la clínica."""
    branch = db_session.query(BranchModel).filter_by(name="Sucursal Test").first()
    if branch:
        return branch

    branch = BranchModel(
        clinic_id=test_clinic.id,
        name="Sucursal Test",
        description="Sucursal de prueba",
        address="Dirección Sucursal Test",
        city="Ciudad Test",
        state="Estado Test",
        country="País Test",
        postal_code="000004",
    )
    db_session.add(branch)
    db_session.flush()
    return branch


@pytest.fixture
def test_owner(db_session, test_clinic):
    """Propietario de prueba vinculado a la clínica."""
    owner = db_session.query(OwnerModel).filter_by(clinic_id=test_clinic.id).first()
    if owner:
        return owner

    user = db_session.query(UserModel).filter_by(email="owner@test.com").first()
    if not user:
        # Generate unique username to avoid constraint conflicts
        unique_suffix = f"{test_clinic.id}_{uuid.uuid4().hex}"
        user = UserModel(
            email=f"owner_test_{unique_suffix}@test.com",
            username=f"owner_unique_{unique_suffix}",
            hashed_password="hashed_password",
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
        db_session.refresh(user)

    owner = OwnerModel(
        user_id=user.id,
        clinic_id=test_clinic.id,
        phone="1234567890",
        first_name="Test",
        last_name="Owner",
        email=f"owner_test_{test_clinic.id}@test.com",
    )
    db_session.add(owner)
    db_session.flush()
    return owner


@pytest.fixture
def test_pet(db_session, test_owner):
    """Mascota de prueba."""
    pet = db_session.query(PetModel).filter_by(name="Max", species="perro").first()
    if pet:
        return pet

    pet = PetModel(owner_id=test_owner.id, name="Max", species="perro")
    db_session.add(pet)
    db_session.flush()
    return pet


def test_create_appointment_success(
    client, authenticated_user, test_clinic, test_branch, test_owner, test_pet
):
    """AC-008-03: Crear una cita exitosamente."""
    response = client.post(
        "/api/v1/appointments",
        json={
            "pet_id": test_pet.id,
            "clinic_id": test_clinic.id,
            "branch_id": test_branch.id,
            "veterinarian_id": None,
            "scheduled_start": "2026-12-31T10:00:00",
            "appointment_type": "consultation",
            "reason": "Consulta general",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["status"] == "pending"
    assert data["appointment_type"] == "consultation"
    assert data["reason"] == "Consulta general"


def test_create_appointment_with_veterinarian(
    client,
    db_session,
    authenticated_user,
    test_clinic,
    test_branch,
    test_owner,
    test_pet,
):
    """AC-008-04: Crear una cita con veterinario asignado."""
    # Crear un veterinario de prueba
    vet = UserModel(
        email="vet_test_vet@test.com",
        username=f"vet_test_{uuid.uuid4().hex}",
        hashed_password="hashed",
        first_name="Dr.",
        last_name="Test",
        is_active=True,
    )
    db_session.add(vet)
    db_session.flush()
    db_session.refresh(vet)

    response = client.post(
        "/api/v1/appointments",
        json={
            "pet_id": test_pet.id,
            "clinic_id": test_clinic.id,
            "branch_id": test_branch.id,
            "veterinarian_id": vet.id,
            "scheduled_start": "2026-12-31T14:00:00",
            "appointment_type": "VACCINATION",
            "reason": "Vacunación",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["veterinarian_id"] == vet.id


def test_create_appointment_past_date(client):
    """AC-008-05 (negativo): No permitir citas en el pasado."""
    response = client.post(
        "/api/v1/appointments",
        json={
            "pet_id": None,
            "clinic_id": 1,
            "branch_id": 1,
            "scheduled_start": "2020-01-01T10:00:00",
            "appointment_type": "consultation",
            "reason": "Test",
        },
    )

    assert response.status_code == 422


def test_create_appointment_invalid_duration(client):
    """AC-008-06 (negativo): Validar duración mínima de 15 minutos."""
    response = client.post(
        "/api/v1/appointments",
        json={
            "pet_id": None,
            "clinic_id": 1,
            "branch_id": 1,
            "scheduled_start": "2026-12-31T10:00:00",
            "duration_minutes": 10,  # Solo 10 minutos (menos del mínimo 15)
            "appointment_type": "consultation",
            "reason": "Test",
        },
    )

    assert response.status_code == 422


def test_create_appointment_unauthenticated(client):
    """AC-008-02 (negativo): Sin autenticación, debe rechazar."""
    # Guardar y remover auth override para este test específico
    from app.core.security import get_current_access_user as auth_dep

    original_override = app.dependency_overrides.get(auth_dep)
    if auth_dep in app.dependency_overrides:
        del app.dependency_overrides[auth_dep]

    try:
        response = client.post(
            "/api/v1/appointments",
            json={
                "pet_id": 1,
                "clinic_id": 1,
                "branch_id": 1,
                "scheduled_start": "2026-12-31T10:00:00",
            },
        )
        assert response.status_code in (401, 403)
    finally:
        # Restaurar el override original
        if original_override:
            app.dependency_overrides[auth_dep] = original_override
