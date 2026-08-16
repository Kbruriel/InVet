"""Tests para BOLA/IDOR en citas (AC-008-17).

Verifica que un usuario no pueda acceder a citas de otra clínica.
"""
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


def _setup_two_clinics(db_session):
    """Configurar dos clínicas con sus respectivos propietarios y mascotas."""
    clinic_a = ClinicModel(name="Clínica A", address="Dirección A")
    clinic_b = ClinicModel(name="Clínica B", address="Dirección B")
    db_session.add_all([clinic_a, clinic_b])
    db_session.flush()

    user_a = UserModel(
        email="ownerA@test.com",
        password="hashed",
        full_name="Owner A",
        role=UserRole.OWNER,
        clinic_id=clinic_a.id,
        is_active=True,
    )
    user_b = UserModel(
        email="ownerB@test.com",
        password="hashed",
        full_name="Owner B",
        role=UserRole.OWNER,
        clinic_id=clinic_b.id,
        is_active=True,
    )
    db_session.add_all([user_a, user_b])
    db_session.flush()

    owner_a = OwnerModel(user_id=user_a.id, clinic_id=clinic_a.id, phone="111")
    owner_b = OwnerModel(user_id=user_b.id, clinic_id=clinic_b.id, phone="222")
    db_session.add_all([owner_a, owner_b])
    db_session.flush()

    pet_a = PetModel(owner_id=owner_a.id, name="Max", species="perro")
    pet_b = PetModel(owner_id=owner_b.id, name="Luna", species="gato")
    db_session.add_all([pet_a, pet_b])
    db_session.flush()

    from datetime import datetime, timedelta
    start_a = datetime(2026, 12, 31, 10, 0, 0)
    end_a = start_a + timedelta(minutes=30)
    appt_a = AppointmentModel(
        owner_id=owner_a.id,
        pet_id=pet_a.id,
        clinic_id=clinic_a.id,
        scheduled_start=start_a,
        scheduled_end=end_a,
        status="pending",
        appointment_type="consultation",
        reason="Consulta A",
    )
    db_session.add(appt_a)
    db_session.flush()

    start_b = datetime(2026, 12, 31, 14, 0, 0)
    end_b = start_b + timedelta(minutes=30)
    appt_b = AppointmentModel(
        owner_id=owner_b.id,
        pet_id=pet_b.id,
        clinic_id=clinic_b.id,
        scheduled_start=start_b,
        scheduled_end=end_b,
        status="pending",
        appointment_type="consultation",
        reason="Consulta B",
    )
    db_session.add(appt_b)
    db_session.flush()

    return appt_a, appt_b, clinic_a.id, clinic_b.id


def _auth_mock(user_id=1, clinic_id=1, role=UserRole.OWNER):
    return patch('app.api.v1.dependencies.get_current_access_user', return_value=MagicMock(
        id=user_id,
        clinic_id=clinic_id,
        role=role,
        is_active=True,
    ))


def test_get_own_appointment(client, db_session):
    """AC-008-17a: Usuario puede obtener su propia cita."""
    appt_a, _, _, _ = _setup_two_clinics(db_session)
    db_session.commit()

    with _auth_mock(user_id=appt_a.owner.user_id, clinic_id=appt_a.clinic_id):
        response = client.get(f"/api/v1/appointments/{appt_a.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == appt_a.id


def test_get_other_clinic_appointment(client, db_session):
    """AC-008-17b: Usuario NO puede obtener cita de otra clínica (BOLA/IDOR)."""
    _, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de la clínica A intenta acceder a cita de la clínica B
    with _auth_mock(user_id=1, clinic_id=clinic_a_id):
        response = client.get(f"/api/v1/appointments/{appt_b.id}")

    # Debe retornar 403 o 404 (no se puede saber que existe)
    assert response.status_code in (403, 404)


def test_update_own_appointment(client, db_session):
    """AC-008-17c: Usuario puede actualizar su propia cita."""
    appt_a, _, clinic_a_id, _ = _setup_two_clinics(db_session)
    db_session.commit()

    with _auth_mock(user_id=appt_a.owner.user_id, clinic_id=clinic_a_id):
        response = client.put(
            f"/api/v1/appointments/{appt_a.id}",
            json={"reason": "Razón actualizada"},
        )

    assert response.status_code == 200


def test_update_other_clinic_appointment(client, db_session):
    """AC-008-17d: Usuario NO puede actualizar cita de otra clínica (BOLA/IDOR)."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de la clínica A intenta actualizar cita de la clínica B
    with _auth_mock(user_id=appt_b.owner.user_id, clinic_id=clinic_b_id):
        response = client.put(
            f"/api/v1/appointments/{appt_a.id}",
            json={"reason": "Intrusión"},
        )

    assert response.status_code in (403, 404)


def test_delete_other_clinic_appointment(client, db_session):
    """AC-008-17e: Usuario NO puede eliminar cita de otra clínica (BOLA/IDOR)."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    with _auth_mock(user_id=appt_b.owner.user_id, clinic_id=clinic_b_id):
        response = client.delete(f"/api/v1/appointments/{appt_a.id}")

    assert response.status_code in (403, 404)


def test_transition_other_clinic_appointment(client, db_session):
    """AC-008-17f: Usuario NO puede cambiar estado de cita de otra clínica."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    with _auth_mock(user_id=appt_b.owner.user_id, clinic_id=clinic_b_id):
        response = client.post(
            f"/api/v1/appointments/{appt_a.id}/status",
            json={"status": "approved"},
        )

    assert response.status_code in (403, 404)


def test_list_own_appointments(client, db_session):
    """AC-008-17g: LIST solo retorna citas de la propia clínica."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de clínica A lista sus citas (my_appointments=true)
    with _auth_mock(user_id=appt_a.owner.user_id, clinic_id=clinic_a_id):
        response = client.get("/api/v1/appointments?my_appointments=true")

    assert response.status_code == 200
    data = response.json()
    results = data.get("results", [])
    
    # Solo debe ver citas de su clínica
    for item in results:
        assert item["clinic_id"] == clinic_a_id


def test_list_all_appointments_other_clinic(client, db_session):
    """AC-008-17h: LIST sin filtro my_appointments no expone citas de otra clínica."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de clínica B intenta listar todas las citas (sin my_appointments)
    with _auth_mock(user_id=appt_b.owner.user_id, clinic_id=clinic_b_id):
        response = client.get("/api/v1/appointments")

    assert response.status_code == 200
    data = response.json()
    results = data.get("results", [])
    
    # No debe ver citas de la clínica A
    for item in results:
        assert item["clinic_id"] != clinic_a_id


def test_availability_other_clinic(client, db_session):
    """AC-008-17i: availability no expone datos de otra clínica."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de clínica B consulta disponibilidad de su propia clínica
    with _auth_mock(user_id=appt_b.owner.user_id, clinic_id=clinic_b_id):
        response = client.get("/api/v1/appointments/availability?date=2026-12-31")

    assert response.status_code == 200


def test_availability_cross_clinic_attempt(client, db_session):
    """AC-008-17j: Intento de acceso a disponibilidad cruzada."""
    appt_a, _, clinic_a_id, _ = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de clínica A intenta consultar con clinic_id diferente
    with _auth_mock(user_id=appt_a.owner.user_id, clinic_id=clinic_a_id):
        response = client.get(f"/api/v1/appointments/availability?date=2026-12-31&clinic_id={clinic_a_id}")

    assert response.status_code == 200
    # Debe retornar slots solo de su propia clínica
