"""Tests para transiciones de estado de citas (AC-008-15, AC-008-16)."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.app import app
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.user import User as UserModel, UserRole
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.pet import Pet as PetModel
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.appointment import Appointment as AppointmentModel


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
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


def _create_test_data(db_session):
    """Crear datos de prueba base."""
    clinic = ClinicModel(name="Clínica Test", address="Dirección Test")
    db_session.add(clinic)
    db_session.flush()

    user = UserModel(
        email="owner@test.com",
        password="hashed",
        full_name="Test Owner",
        role=UserRole.OWNER,
        clinic_id=clinic.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    owner = OwnerModel(user_id=user.id, clinic_id=clinic.id, phone="1234567890")
    db_session.add(owner)
    db_session.flush()

    pet = PetModel(owner_id=owner.id, name="Max", species="perro")
    db_session.add(pet)
    db_session.flush()

    from datetime import datetime, timedelta
    start = datetime(2026, 12, 31, 10, 0, 0)
    end = start + timedelta(minutes=30)

    appt = AppointmentModel(
        owner_id=owner.id,
        pet_id=pet.id,
        clinic_id=clinic.id,
        scheduled_start=start,
        scheduled_end=end,
        status="pending",
        appointment_type="consultation",
        reason="Consulta general",
    )
    db_session.add(appt)
    db_session.flush()
    return appt


def _auth_mock(user_id=1, clinic_id=1, role=UserRole.OWNER):
    return patch('app.api.v1.dependencies.get_current_access_user', return_value=MagicMock(
        id=user_id,
        clinic_id=clinic_id,
        role=role,
        is_active=True,
    ))


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
    end = start + timedelta(minutes=30)
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
    end = start + timedelta(minutes=30)
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
    end = start + timedelta(minutes=30)
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
    end = start + timedelta(minutes=30)
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
    end = start + timedelta(minutes=30)
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
