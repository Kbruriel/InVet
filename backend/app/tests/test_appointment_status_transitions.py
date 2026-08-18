"""Tests para transiciones de estado de citas (AC-008-15, AC-008-16)."""

import uuid
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.app import app
from app.domain.user import UserRole

# Sobrescribir el engine global de session.py con SQLite en memoria ANTES de importar la app
from app.infrastructure.database import session as session_module
from app.infrastructure.database.models.appointment import (
    Appointment as AppointmentModel,
)
from app.infrastructure.database.models.branch import Branch as BranchModel
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.pet import Pet as PetModel
from app.infrastructure.database.models.user import User as UserModel
from app.infrastructure.database.session import Base, get_db

test_engine = create_engine(
    "sqlite:///:memory:",
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


@pytest.fixture(scope="module")
def client():
    """Cliente con auth override para pruebas de transiciones."""
    from app.api.v1.routers.appointment_router import get_current_db as router_get_db
    from app.core.security import get_current_access_user as auth_dep

    def override_auth():
        return {
            "id": 1,
            "user_id": 1,
            "email": "owner@test.com",
            "username": "owner_test_001",
            "role": UserRole.OWNER.value,
            "clinic_id": 1,
            "is_active": True,
        }

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth_dep] = override_auth
    # Also override the router's local dependency reference
    app.dependency_overrides[router_get_db] = override_get_db

    Base.metadata.create_all(bind=test_engine)
    return TestClient(app)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


def _create_test_data(db_session):
    """Crear datos de prueba base. Función idempotente."""
    # Verificar si ya existe la clínica
    clinic = db_session.query(ClinicModel).filter_by(name="Clínica Test").first()
    if not clinic:
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

    # Verificar si ya existe la sucursal
    branch = db_session.query(BranchModel).filter_by(name="Sucursal Test").first()
    if not branch:
        branch = BranchModel(
            clinic_id=clinic.id,
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

    # Generar sufijo único para evitar conflictos de email/username
    unique_suffix = f"status_{uuid.uuid4().hex}"

    user = (
        db_session.query(UserModel).filter_by(username=f"owner_{unique_suffix}").first()
    )
    if not user:
        user = UserModel(
            email=f"owner_{unique_suffix}@test.com",
            username=f"owner_{unique_suffix}",
            hashed_password="hashed_password",
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

    owner = (
        db_session.query(OwnerModel)
        .filter_by(email=f"owner_{unique_suffix}@test.com")
        .first()
    )
    if not owner:
        owner = OwnerModel(
            user_id=user.id,
            clinic_id=clinic.id,
            phone="1234567890",
            first_name="Test",
            last_name="Owner",
            email=f"owner_{unique_suffix}@test.com",
        )
        db_session.add(owner)
        db_session.flush()

    pet = db_session.query(PetModel).filter_by(name="Max", owner_id=owner.id).first()
    if not pet:
        pet = PetModel(owner_id=owner.id, name="Max", species="perro")
        db_session.add(pet)
        db_session.flush()

    from datetime import datetime, timedelta

    start = datetime(2026, 12, 31, 10, 0, 0)
    _end = start + timedelta(minutes=30)

    appt = (
        db_session.query(AppointmentModel)
        .filter_by(owner_id=owner.id, pet_id=pet.id, scheduled_start=start)
        .first()
    )
    if not appt:
        appt = AppointmentModel(
            owner_id=owner.id,
            pet_id=pet.id,
            clinic_id=clinic.id,
            branch_id=branch.id,
            scheduled_start=start,
            scheduled_end=_end,
            status="pending",
            appointment_type="consultation",
            reason="Consulta general",
        )
        db_session.add(appt)
        db_session.flush()
    return appt


@contextmanager
def _auth_mock(user_id=1, clinic_id=1, role=UserRole.OWNER):
    """Override la autenticación (get_current_access_user) sin tocar la sesión de BD."""
    from app.core.security import get_current_access_user as auth_dep

    mock_user = {
        "id": user_id,
        "user_id": user_id,
        "email": "owner@test.com",
        "username": "owner_test_001",
        "role": role.value,
        "clinic_id": clinic_id,
        "is_active": True,
    }

    from app.api.v1.app import app as fastapi_app

    original = fastapi_app.dependency_overrides.get(auth_dep)

    fastapi_app.dependency_overrides[auth_dep] = lambda: mock_user

    try:
        yield mock_user
    finally:
        # Restore original
        if original is not None:
            fastapi_app.dependency_overrides[auth_dep] = original
        elif auth_dep in fastapi_app.dependency_overrides:
            del fastapi_app.dependency_overrides[auth_dep]


def test_transition_pending_to_approved(client, db_session):
    """AC-008-15a: pending → approved."""
    appt = _create_test_data(db_session)
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "approved"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


def test_transition_approved_to_confirmed(client, db_session):
    """AC-008-15b: approved → confirmed."""
    # Primero aprobar la cita
    appt = _create_test_data(db_session)
    from datetime import datetime, timedelta

    start = datetime(2026, 12, 31, 10, 0, 0)
    _end = start + timedelta(minutes=30)
    appt.status = "approved"
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "confirmed"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"


def test_transition_confirmed_to_completed(client, db_session):
    """AC-008-15c: confirmed → completed."""
    appt = _create_test_data(db_session)
    from datetime import datetime, timedelta

    start = datetime(2026, 12, 31, 10, 0, 0)
    _end = start + timedelta(minutes=30)
    appt.status = "confirmed"
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "completed"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_transition_confirmed_to_no_show(client, db_session):
    """AC-008-15d: confirmed → no_show."""
    appt = _create_test_data(db_session)
    from datetime import datetime, timedelta

    start = datetime(2026, 12, 31, 10, 0, 0)
    _end = start + timedelta(minutes=30)
    appt.status = "confirmed"
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "no_show"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_show"


def test_invalid_transition_pending_to_confirmed(client, db_session):
    """AC-008-16 (negativo): pending no puede saltar a confirmed."""
    appt = _create_test_data(db_session)
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "confirmed"},  # Salta approved
        )

    assert response.status_code == 422


def test_invalid_transition_completed_to_anything(client, db_session):
    """AC-008-16 (negativo): completed es estado terminal."""
    appt = _create_test_data(db_session)
    from datetime import datetime, timedelta

    start = datetime(2026, 12, 31, 10, 0, 0)
    _end = start + timedelta(minutes=30)
    appt.status = "completed"
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "confirmed"},  # No se puede revertir
        )

    assert response.status_code == 422


def test_transition_cancelled_from_pending(client, db_session):
    """AC-008-15e: pending → cancelled es válido."""
    appt = _create_test_data(db_session)
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "cancelled"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


def test_transition_confirmed_to_rescheduled(client, db_session):
    """AC-008-15f: confirmed → rescheduled es válido."""
    appt = _create_test_data(db_session)
    from datetime import datetime, timedelta

    start = datetime(2026, 12, 31, 10, 0, 0)
    _end = start + timedelta(minutes=30)
    appt.status = "confirmed"
    db_session.commit()

    with _auth_mock():
        response = client.post(
            f"/api/v1/appointments/{appt.id}/status",
            json={"status": "rescheduled"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rescheduled"


def test_transition_with_nonexistent_appointment(client):
    """Transición con cita inexistente retorna 404."""
    with _auth_mock():
        response = client.post(
            "/api/v1/appointments/99999/status",
            json={"status": "approved"},
        )

    assert response.status_code == 404
