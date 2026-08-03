"""Tests API para autenticacion."""

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.core.security import verify_password
from app.infrastructure.database import get_db
from app.infrastructure.database.models.user import User as UserModel


@pytest.fixture
def client(db_session):
    """Cliente FastAPI con base aislada para auth."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_user(client: TestClient, email: str = "ada@example.com"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "firstName": "Ada",
            "lastName": "Lovelace",
        },
    )


def test_register_auth_user_returns_tokens_and_hashes_password(client, db_session):
    response = register_user(client)

    assert response.status_code == 201
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]

    db_user = (
        db_session.query(UserModel).filter(UserModel.email == "ada@example.com").one()
    )
    assert db_user.first_name == "Ada"
    assert db_user.last_name == "Lovelace"
    assert db_user.hashed_password != "secret123"
    assert verify_password("secret123", db_user.hashed_password)


def test_register_rejects_duplicate_email(client):
    first_response = register_user(client)
    second_response = register_user(client)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Ya existe un usuario con ese correo"


def test_login_returns_tokens_for_valid_credentials(client):
    register_user(client, email="login@example.com")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


def test_login_rejects_invalid_password(client):
    register_user(client, email="invalid@example.com")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@example.com", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales invalidas"


def test_me_requires_authorization(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_returns_authenticated_profile(client):
    register_response = register_user(client, email="profile@example.com")
    access_token = register_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "profile@example.com",
        "firstName": "Ada",
        "lastName": "Lovelace",
        "role": "user",
    }


def test_refresh_returns_new_tokens_for_valid_refresh_token(client):
    register_response = register_user(client, email="refresh@example.com")
    refresh_token = register_response.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


def test_refresh_rejects_access_token(client):
    register_response = register_user(client, email="access@example.com")
    access_token = register_response.json()["access_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token invalido"
