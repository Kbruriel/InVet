"""Pruebas de integracion para propietarios y mascotas."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.infrastructure.database.models.user import User as UserDB
from app.infrastructure.database.session import get_db
from app.infrastructure.models.clinic_models import ClinicDB


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


def _auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer 1"}


def _seed_access_context(db_session):
    admin = UserDB(
        id=1,
        email="admin@example.com",
        username="admin",
        hashed_password="hashed",
        is_active=True,
        is_admin=True,
    )
    clinic_1 = ClinicDB(
        name="Clinic One",
        description="Primary clinic",
        address="Main St 1",
        city="City",
        state="State",
        country="Country",
        postal_code="00001",
        phone="555-0101",
        email="clinic1@example.com",
        is_active=True,
    )
    clinic_2 = ClinicDB(
        name="Clinic Two",
        description="Secondary clinic",
        address="Main St 2",
        city="City",
        state="State",
        country="Country",
        postal_code="00002",
        phone="555-0102",
        email="clinic2@example.com",
        is_active=True,
    )

    db_session.add(admin)
    db_session.add(clinic_1)
    db_session.add(clinic_2)
    db_session.commit()
    db_session.refresh(clinic_1)
    db_session.refresh(clinic_2)
    return clinic_1, clinic_2


def _create_owner(client: TestClient, clinic_id: int, email: str):
    response = client.post(
        "/api/v1/owners/",
        json={
            "first_name": "Test",
            "last_name": "Owner",
            "email": email,
            "clinic_id": clinic_id,
            "phone": "555-0000",
        },
        headers=_auth_headers(),
    )
    assert response.status_code == 201
    return response.json()


def _create_pet(client: TestClient, owner_id: int, name: str, history: bool = False):
    response = client.post(
        "/api/v1/pets/",
        json={
            "owner_id": owner_id,
            "name": name,
            "species": "Dog",
            "breed": "Labrador",
            "color": "Brown",
            "gender": "male",
            "weight": "20",
            "date_of_birth": datetime.utcnow().isoformat(),
            "has_medical_history": history,
        },
        headers=_auth_headers(),
    )
    assert response.status_code == 201
    return response.json()


def test_get_owners_returns_pagination(client, db_session):
    _seed_access_context(db_session)
    _create_owner(client, 1, "owner1@example.com")
    _create_owner(client, 1, "owner2@example.com")
    _create_owner(client, 2, "owner3@example.com")

    response = client.get("/api/v1/owners/?skip=0&limit=2", headers=_auth_headers())

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 3
    assert len(data["items"]) == 2


def test_delete_owner_with_pets_conflict(client, db_session):
    _seed_access_context(db_session)
    owner = _create_owner(client, 1, "owner4@example.com")
    _create_pet(client, owner["id"], "Milo")

    response = client.delete(f"/api/v1/owners/{owner['id']}", headers=_auth_headers())

    assert response.status_code == 409


def test_get_pets_filters_by_owner_and_breed(client, db_session):
    _seed_access_context(db_session)
    owner_a = _create_owner(client, 1, "owner5@example.com")
    owner_b = _create_owner(client, 2, "owner6@example.com")
    _create_pet(client, owner_a["id"], "Rex")
    _create_pet(client, owner_a["id"], "Luna")
    _create_pet(client, owner_b["id"], "Coco")

    response = client.get(
        f"/api/v1/pets/?owner_id={owner_a['id']}&breed=Labrador",
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 2
    assert len(data["items"]) == 2


def test_delete_pet_with_medical_history_conflict(client, db_session):
    _seed_access_context(db_session)
    owner = _create_owner(client, 1, "owner7@example.com")
    pet = _create_pet(client, owner["id"], "Bruno", history=True)

    response = client.delete(f"/api/v1/pets/{pet['id']}", headers=_auth_headers())

    assert response.status_code == 409
