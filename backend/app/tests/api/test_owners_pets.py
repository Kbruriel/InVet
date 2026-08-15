"""Tests API para propietarios y mascotas (slice 007)."""

from fastapi.testclient import TestClient

from app.api.main import app
from app.api.v1.routers.owners import get_current_db as get_owners_db
from app.api.v1.routers.pets import get_current_db as get_pets_db
from app.core.security import get_current_access_user
from app.infrastructure.database import get_db
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.pet import Pet as PetModel


def _override_auth(user_id: int, role: str = "owner"):
    def _dependency() -> dict:
        return {"id": user_id, "role": role}

    return _dependency


def _build_client(db_session, user_id: int, role: str = "owner") -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_owners_db] = override_get_db
    app.dependency_overrides[get_pets_db] = override_get_db
    app.dependency_overrides[get_current_access_user] = _override_auth(user_id, role)
    return TestClient(app)


def test_list_my_pets_returns_page_size_meta(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.flush()

    pet = PetModel(
        owner_id=owner.id,
        name="Milo",
        species="perro",
        breed="Mestizo",
        weight="12.5",
    )
    db_session.add(pet)
    db_session.commit()

    client = _build_client(db_session, user_id=11)
    with client:
        response = client.get("/api/v1/owners/me/pets")

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["page"] == 1
    assert data["meta"]["page_size"] == 20
    assert data["meta"]["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["nombre"] == "Milo"


def test_list_my_pets_paginates_results(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.flush()

    for index in range(6):
        db_session.add(
            PetModel(
                owner_id=owner.id,
                name=f"Milo {index + 1}",
                species="perro",
                breed="Mestizo",
                weight="12.5",
            )
        )
    db_session.commit()

    client = _build_client(db_session, user_id=11)
    with client:
        response = client.get("/api/v1/owners/me/pets?page=2&page_size=5")

    assert response.status_code == 200
    data = response.json()
    assert data["meta"]["page"] == 2
    assert data["meta"]["page_size"] == 5
    assert data["meta"]["pages"] == 2
    assert len(data["items"]) == 1


def test_create_owner_profile_returns_created_owner(db_session):
    client = _build_client(db_session, user_id=11)
    with client:
        response = client.post(
            "/api/v1/owners",
            json={
                "nombre": "Ana Perez",
                "email": "ana@example.com",
                "telefono": "809-555-0100",
                "direccion": "Calle 1",
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == 11
    assert data["nombre"] == "Ana Perez"
    assert data["email"] == "ana@example.com"


def test_update_owner_profile_updates_allowed_fields(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.commit()

    client = _build_client(db_session, user_id=11)
    with client:
        response = client.put(
            "/api/v1/owners/me",
            json={
                "nombre": "Ana Maria Perez",
                "email": "ana.maria@example.com",
                "telefono": "809-555-1111",
                "direccion": "Calle 2",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Ana Maria Perez"
    assert data["email"] == "ana.maria@example.com"
    assert data["telefono"] == "809-555-1111"
    assert data["direccion"] == "Calle 2"


def test_create_pet_update_and_delete_flow(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.commit()

    client = _build_client(db_session, user_id=11)
    with client:
        create_response = client.post(
            "/api/v1/owners/me/pets",
            json={
                "nombre": "Milo",
                "especie": "perro",
                "raza": "Mestizo",
                "edad": 4,
                "peso": 12.5,
                "fecha_nacimiento": "2026-08-13",
            },
        )

        assert create_response.status_code == 201
        assert create_response.json()["fecha_nacimiento"] == "2026-08-13"
        pet_id = create_response.json()["id"]

        update_response = client.put(
            f"/api/v1/pets/{pet_id}",
            json={
                "nombre": "Milo 2",
                "especie": "perro",
                "raza": "Mestizo",
                "edad": 5,
                "peso": 13.0,
                "fecha_nacimiento": "2026-08-14",
            },
        )

        assert update_response.status_code == 200
        assert update_response.json()["nombre"] == "Milo 2"
        assert update_response.json()["fecha_nacimiento"] == "2026-08-14"

        delete_response = client.delete(f"/api/v1/pets/{pet_id}")
        assert delete_response.status_code == 204

        get_after_delete_response = client.get(f"/api/v1/pets/{pet_id}")

    assert get_after_delete_response.status_code == 404


def test_other_owner_cannot_access_pet_details(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    other_owner = OwnerModel(
        first_name="Luis",
        last_name="Gomez",
        email="luis@example.com",
        phone="809-555-0200",
        address="Calle 2",
        user_id=22,
        clinic_id=22,
    )
    db_session.add_all([owner, other_owner])
    db_session.flush()

    pet = PetModel(
        owner_id=owner.id,
        name="Milo",
        species="perro",
        breed="Mestizo",
        weight="12.5",
    )
    db_session.add(pet)
    db_session.commit()

    client = _build_client(db_session, user_id=22)
    with client:
        response = client.get(f"/api/v1/pets/{pet.id}")

    assert response.status_code == 403


def test_clinic_role_can_access_pet_details(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.flush()

    pet = PetModel(
        owner_id=owner.id,
        name="Milo",
        species="perro",
        breed="Mestizo",
        weight="12.5",
    )
    db_session.add(pet)
    db_session.commit()

    client = _build_client(db_session, user_id=99, role="clinic")
    with client:
        response = client.get(f"/api/v1/pets/{pet.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pet.id
    assert data["nombre"] == "Milo"


def test_clinic_role_can_access_pet_history(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.flush()

    pet = PetModel(
        owner_id=owner.id,
        name="Milo",
        species="perro",
        breed="Mestizo",
        weight="12.5",
    )
    db_session.add(pet)
    db_session.commit()

    client = _build_client(db_session, user_id=99, role="clinic")
    with client:
        response = client.get(f"/api/v1/pets/{pet.id}/history")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["page"] == 1
    assert data["meta"]["page_size"] == 20
    assert data["meta"]["total"] == 0


def test_create_pet_rejects_invalid_species(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.commit()

    client = _build_client(db_session, user_id=11)
    with client:
        response = client.post(
            "/api/v1/owners/me/pets",
            json={
                "nombre": "Milo",
                "especie": "dragon",
                "raza": "Mestizo",
                "edad": 4,
            },
        )

    assert response.status_code == 422


def test_pet_history_returns_empty_list_for_owner(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    db_session.add(owner)
    db_session.flush()

    pet = PetModel(
        owner_id=owner.id,
        name="Milo",
        species="perro",
        breed="Mestizo",
        weight="12.5",
    )
    db_session.add(pet)
    db_session.commit()

    client = _build_client(db_session, user_id=11)
    with client:
        response = client.get(f"/api/v1/pets/{pet.id}/history")

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["meta"]["page"] == 1
    assert data["meta"]["page_size"] == 20
    assert data["meta"]["total"] == 0


def test_pet_history_blocks_other_owner(db_session):
    owner = OwnerModel(
        first_name="Ana",
        last_name="Perez",
        email="ana@example.com",
        phone="809-555-0100",
        address="Calle 1",
        user_id=11,
        clinic_id=11,
    )
    other_owner = OwnerModel(
        first_name="Luis",
        last_name="Gomez",
        email="luis@example.com",
        phone="809-555-0200",
        address="Calle 2",
        user_id=22,
        clinic_id=22,
    )
    db_session.add_all([owner, other_owner])
    db_session.flush()

    pet = PetModel(
        owner_id=owner.id,
        name="Milo",
        species="perro",
        breed="Mestizo",
        weight="12.5",
    )
    db_session.add(pet)
    db_session.commit()

    client = _build_client(db_session, user_id=22)
    with client:
        response = client.get(f"/api/v1/pets/{pet.id}/history")

    assert response.status_code == 403
