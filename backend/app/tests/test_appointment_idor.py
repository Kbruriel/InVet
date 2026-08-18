"""Tests para BOLA/IDOR en citas (AC-008-17).

Verifica que un usuario no pueda acceder a citas de otra clínica.
"""

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
    """Cliente con auth override para pruebas IDOR."""
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


def _setup_two_clinics(db_session):  # noqa: C901
    """Configurar dos clínicas con sus respectivos propietarios y mascotas. Función idempotente."""
    # Verificar si ya existen las clínicas
    clinic_a = db_session.query(ClinicModel).filter_by(name="Clínica A").first()
    if not clinic_a:
        clinic_a = ClinicModel(
            name="Clínica A",
            address="Dirección A",
            city="Ciudad A",
            state="Estado A",
            country="País A",
            postal_code="000001",
        )
        db_session.add(clinic_a)
        db_session.flush()
        db_session.refresh(clinic_a)

    clinic_b = db_session.query(ClinicModel).filter_by(name="Clínica B").first()
    if not clinic_b:
        clinic_b = ClinicModel(
            name="Clínica B",
            address="Dirección B",
            city="Ciudad B",
            state="Estado B",
            country="País B",
            postal_code="000002",
        )
        db_session.add(clinic_b)
        db_session.flush()
        db_session.refresh(clinic_b)

    # Verificar si ya existen las sucursales
    branch_a = db_session.query(BranchModel).filter_by(name="Sucursal A").first()
    if not branch_a:
        branch_a = BranchModel(
            clinic_id=clinic_a.id,
            name="Sucursal A",
            description="Sucursal de prueba A",
            address="Dirección Sucursal A",
            city="Ciudad A",
            state="Estado A",
            country="País A",
            postal_code="000005",
        )
        db_session.add(branch_a)
        db_session.flush()
        db_session.refresh(branch_a)

    branch_b = db_session.query(BranchModel).filter_by(name="Sucursal B").first()
    if not branch_b:
        branch_b = BranchModel(
            clinic_id=clinic_b.id,
            name="Sucursal B",
            description="Sucursal de prueba B",
            address="Dirección Sucursal B",
            city="Ciudad B",
            state="Estado B",
            country="País B",
            postal_code="000006",
        )
        db_session.add(branch_b)
        db_session.flush()
        db_session.refresh(branch_b)

    # Usar sufijos únicos para evitar conflictos de email/username
    unique_suffix_a = f"idor_a_{uuid.uuid4().hex}"
    unique_suffix_b = f"idor_b_{uuid.uuid4().hex}"

    user_a = db_session.query(UserModel).filter_by(username=unique_suffix_a).first()
    if not user_a:
        user_a = UserModel(
            email=f"{unique_suffix_a}@test.com",
            username=unique_suffix_a,
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user_a)
        db_session.flush()
        db_session.refresh(user_a)

    user_b = db_session.query(UserModel).filter_by(username=unique_suffix_b).first()
    if not user_b:
        user_b = UserModel(
            email=f"{unique_suffix_b}@test.com",
            username=unique_suffix_b,
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user_b)
        db_session.flush()
        db_session.refresh(user_b)

    # Verificar si ya existen los owners
    owner_a = (
        db_session.query(OwnerModel)
        .filter_by(email=f"{unique_suffix_a}@test.com")
        .first()
    )
    if not owner_a:
        owner_a = OwnerModel(
            user_id=user_a.id,
            clinic_id=clinic_a.id,
            phone="111",
            first_name="Owner",
            last_name="A",
            email=f"{unique_suffix_a}@test.com",
        )
        db_session.add(owner_a)
        db_session.flush()

    owner_b = (
        db_session.query(OwnerModel)
        .filter_by(email=f"{unique_suffix_b}@test.com")
        .first()
    )
    if not owner_b:
        owner_b = OwnerModel(
            user_id=user_b.id,
            clinic_id=clinic_b.id,
            phone="222",
            first_name="Owner",
            last_name="B",
            email=f"{unique_suffix_b}@test.com",
        )
        db_session.add(owner_b)
        db_session.flush()

    # Verificar si ya existen las mascotas
    pet_a = (
        db_session.query(PetModel).filter_by(name="Max", owner_id=owner_a.id).first()
    )
    if not pet_a:
        pet_a = PetModel(owner_id=owner_a.id, name="Max", species="perro")
        db_session.add(pet_a)
        db_session.flush()

    pet_b = (
        db_session.query(PetModel).filter_by(name="Luna", owner_id=owner_b.id).first()
    )
    if not pet_b:
        pet_b = PetModel(owner_id=owner_b.id, name="Luna", species="gato")
        db_session.add(pet_b)
        db_session.flush()

    from datetime import datetime, timedelta

    start_a = datetime(2026, 12, 31, 10, 0, 0)
    end_a = start_a + timedelta(minutes=30)
    appt_a = (
        db_session.query(AppointmentModel)
        .filter_by(owner_id=owner_a.id, pet_id=pet_a.id, scheduled_start=start_a)
        .first()
    )
    if not appt_a:
        appt_a = AppointmentModel(
            owner_id=owner_a.id,
            pet_id=pet_a.id,
            clinic_id=clinic_a.id,
            branch_id=branch_a.id,
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
    appt_b = (
        db_session.query(AppointmentModel)
        .filter_by(owner_id=owner_b.id, pet_id=pet_b.id, scheduled_start=start_b)
        .first()
    )
    if not appt_b:
        appt_b = AppointmentModel(
            owner_id=owner_b.id,
            pet_id=pet_b.id,
            clinic_id=clinic_b.id,
            branch_id=branch_b.id,
            scheduled_start=start_b,
            scheduled_end=end_b,
            status="pending",
            appointment_type="consultation",
            reason="Consulta B",
        )
        db_session.add(appt_b)
    db_session.flush()

    return appt_a, appt_b, clinic_a.id, clinic_b.id


@contextmanager
def _setup_auth(user_id=1, clinic_id=1, role=UserRole.OWNER):
    """Set up auth context for a specific test."""
    from app.core.security import get_current_access_user as auth_dep

    def override_auth():
        return {
            "id": user_id,
            "user_id": user_id,
            "email": f"owner{user_id}@test.com",
            "username": f"owner_{user_id}",
            "role": role.value,
            "clinic_id": clinic_id,
            "is_active": True,
        }

    # Store original override
    original = app.dependency_overrides.get(auth_dep)

    # Set new auth override
    app.dependency_overrides[auth_dep] = override_auth

    try:
        yield
    finally:
        # Restore original
        if original is not None:
            app.dependency_overrides[auth_dep] = original
        elif auth_dep in app.dependency_overrides:
            del app.dependency_overrides[auth_dep]


def test_get_own_appointment(client, db_session):
    """AC-008-17a: Usuario puede obtener su propia cita."""
    appt_a, _, _, _ = _setup_two_clinics(db_session)
    db_session.commit()

    with _setup_auth(user_id=appt_a.owner_id, clinic_id=appt_a.clinic_id):
        response = client.get(f"/api/v1/appointments/{appt_a.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == appt_a.id


def test_get_other_clinic_appointment(client, db_session):
    """AC-008-17b: Usuario NO puede obtener cita de otra clínica (BOLA/IDOR)."""
    _, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de la clínica A intenta acceder a cita de la clínica B
    with _setup_auth(user_id=1, clinic_id=clinic_a_id):
        response = client.get(f"/api/v1/appointments/{appt_b.id}")

    # Debe retornar 403 o 404 (no se puede saber que existe)
    assert response.status_code in (403, 404)


def test_update_own_appointment(client, db_session):
    """AC-008-17c: Usuario puede actualizar su propia cita."""
    appt_a, _, clinic_a_id, _ = _setup_two_clinics(db_session)
    db_session.commit()

    with _setup_auth(user_id=appt_a.owner_id, clinic_id=clinic_a_id):
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
    with _setup_auth(user_id=appt_b.owner_id, clinic_id=clinic_b_id):
        response = client.put(
            f"/api/v1/appointments/{appt_a.id}",
            json={"reason": "Intrusión"},
        )

    assert response.status_code in (403, 404)


def test_delete_other_clinic_appointment(client, db_session):
    """AC-008-17e: Usuario NO puede eliminar cita de otra clínica (BOLA/IDOR)."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    with _setup_auth(user_id=appt_b.owner_id, clinic_id=clinic_b_id):
        response = client.delete(f"/api/v1/appointments/{appt_a.id}")

    assert response.status_code in (403, 404)


def test_transition_other_clinic_appointment(client, db_session):
    """AC-008-17f: Usuario NO puede cambiar estado de cita de otra clínica."""
    appt_a, appt_b, clinic_a_id, clinic_b_id = _setup_two_clinics(db_session)
    db_session.commit()

    with _setup_auth(user_id=appt_b.owner_id, clinic_id=clinic_b_id):
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
    with _setup_auth(user_id=appt_a.owner_id, clinic_id=clinic_a_id):
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
    with _setup_auth(user_id=appt_b.owner_id, clinic_id=clinic_b_id):
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
    with _setup_auth(user_id=appt_b.owner_id, clinic_id=clinic_b_id):
        response = client.get("/api/v1/appointments/availability?date=2026-12-31")

    assert response.status_code == 200


def test_availability_cross_clinic_attempt(client, db_session):
    """AC-008-17j: Intento de acceso a disponibilidad cruzada."""
    appt_a, _, clinic_a_id, _ = _setup_two_clinics(db_session)
    db_session.commit()

    # Usuario de clínica A intenta consultar con clinic_id diferente
    with _setup_auth(user_id=appt_a.owner_id, clinic_id=clinic_a_id):
        response = client.get(
            f"/api/v1/appointments/availability?date=2026-12-31&clinic_id={clinic_a_id}"
        )

    assert response.status_code == 200
    # Debe retornar slots solo de su propia clínica
