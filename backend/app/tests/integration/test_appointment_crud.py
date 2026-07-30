"""
Pruebas de integracion para la funcionalidad de citas.
"""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.core.security import create_access_token
from app.infrastructure.database.models.appointment import AppointmentSlot
from app.infrastructure.database.models.owner import Owner
from app.infrastructure.database.session import get_db


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()


def _auth_headers(user_id: int = 1) -> dict[str, str]:
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _seed_owner_and_slots(db_session, owner_id: int = 1):
    owner = Owner(
        id=owner_id,
        first_name="Test",
        last_name="Owner",
        email=f"owner{owner_id}@example.com",
        is_active=True,
    )
    slot_1 = AppointmentSlot(
        clinic_id=1,
        branch_id=1,
        start_time=datetime.utcnow() + timedelta(hours=1),
        end_time=datetime.utcnow() + timedelta(hours=2),
        is_available=True,
    )
    slot_2 = AppointmentSlot(
        clinic_id=1,
        branch_id=1,
        start_time=datetime.utcnow() + timedelta(hours=3),
        end_time=datetime.utcnow() + timedelta(hours=4),
        is_available=True,
    )

    db_session.add(owner)
    db_session.add(slot_1)
    db_session.add(slot_2)
    db_session.commit()
    db_session.refresh(slot_1)
    db_session.refresh(slot_2)
    return owner, slot_1, slot_2


def _create_appointment(client: TestClient, slot_id: int, headers: dict[str, str]):
    response = client.post(
        "/api/v1/appointments/",
        json={
            "owner_id": 1,
            "clinic_id": 1,
            "branch_id": 1,
            "appointment_slot_id": slot_id,
            "scheduled_date": datetime.utcnow().isoformat(),
        },
        headers=headers,
    )
    assert response.status_code == 200
    return response.json()


def test_create_appointment_success(client, db_session):
    _seed_owner_and_slots(db_session)

    response = client.post(
        "/api/v1/appointments/",
        json={
            "owner_id": 1,
            "clinic_id": 1,
            "branch_id": 1,
            "appointment_slot_id": 1,
            "scheduled_date": datetime.utcnow().isoformat(),
        },
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["owner_id"] == 1
    assert data["status"] == "pending"
    assert data["clinic_id"] == 1


def test_create_appointment_invalid_slot(client, db_session):
    _seed_owner_and_slots(db_session)

    response = client.post(
        "/api/v1/appointments/",
        json={
            "owner_id": 1,
            "clinic_id": 1,
            "branch_id": 1,
            "appointment_slot_id": 999,
            "scheduled_date": datetime.utcnow().isoformat(),
        },
        headers=_auth_headers(),
    )

    assert response.status_code == 400


def test_get_appointment(client, db_session):
    _seed_owner_and_slots(db_session)
    created = _create_appointment(client, 1, _auth_headers())

    response = client.get(
        f"/api/v1/appointments/{created['id']}",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["owner_id"] == 1


def test_cancel_appointment(client, db_session):
    _seed_owner_and_slots(db_session)
    created = _create_appointment(client, 1, _auth_headers())

    response = client.put(
        f"/api/v1/appointments/{created['id']}/cancel",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_confirm_appointment(client, db_session):
    _seed_owner_and_slots(db_session)
    created = _create_appointment(client, 1, _auth_headers())

    response = client.put(
        f"/api/v1/appointments/{created['id']}/confirm",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


def test_reschedule_appointment(client, db_session):
    _seed_owner_and_slots(db_session)
    created = _create_appointment(client, 1, _auth_headers())

    response = client.put(
        f"/api/v1/appointments/{created['id']}/reschedule?new_slot_id=2",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["appointment_slot_id"] == 2


def test_mark_no_show(client, db_session):
    _seed_owner_and_slots(db_session)
    created = _create_appointment(client, 1, _auth_headers())

    confirm_response = client.put(
        f"/api/v1/appointments/{created['id']}/confirm",
        headers=_auth_headers(),
    )
    assert confirm_response.status_code == 200

    response = client.put(
        f"/api/v1/appointments/{created['id']}/no-show",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "no_show"


def test_complete_appointment(client, db_session):
    _seed_owner_and_slots(db_session)
    created = _create_appointment(client, 1, _auth_headers())

    confirm_response = client.put(
        f"/api/v1/appointments/{created['id']}/confirm",
        headers=_auth_headers(),
    )
    assert confirm_response.status_code == 200

    response = client.put(
        f"/api/v1/appointments/{created['id']}/complete",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_user_appointments(client, db_session):
    _seed_owner_and_slots(db_session)
    _create_appointment(client, 1, _auth_headers())
    _create_appointment(client, 2, _auth_headers())

    response = client.get(
        "/api/v1/appointments/users/1/appointments",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["appointments"]) == 2


def test_get_available_slots(client, db_session):
    _seed_owner_and_slots(db_session)
    _create_appointment(client, 1, _auth_headers())

    response = client.get(
        "/api/v1/appointments/clinics/1/branches/1/availability",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
