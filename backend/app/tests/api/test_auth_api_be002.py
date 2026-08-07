"""Tests API para logout y password reset (BE-002)."""

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.infrastructure.database import get_db


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


def register_user(client: TestClient, email: str = "logout@example.com"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "firstName": "Test",
            "lastName": "User",
        },
    )


def test_logout_returns_generic_message(client):
    """Logout devuelve mensaje generico sin exponer informacion."""
    response = register_user(client)
    assert response.status_code == 201
    data = response.json()

    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": data["refresh_token"]},
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert (
        "sesion" in result["message"].lower() or "cerrada" in result["message"].lower()
    )


def test_logout_without_refresh_token(client):
    """Logout sin refresh token tambien funciona."""
    response = register_user(client)
    assert response.status_code == 201
    data = response.json()

    response = client.post(
        "/api/v1/auth/logout",
        json={},
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200


def test_request_password_reset_returns_generic_message(client):
    """Solicitud de reset devuelve mensaje generico."""
    register_user(client, email="reset@example.com")

    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "reset@example.com"},
    )

    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    # No debe enumerar correos
    assert "reset@example.com" not in result["message"]


def test_request_password_reset_nonexistent_email(client):
    """Solicitud de reset para email inexistente tambien devuelve generico."""
    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "nonexistent@example.com"},
    )

    assert response.status_code == 200
    result = response.json()
    assert "message" in result


def test_confirm_password_reset_with_invalid_token(client):
    """Confirmar reset con token invalido devuelve 401."""
    response = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "reset_token": "invalid.token.here",
            "new_password": "newpass123",
        },
    )

    assert response.status_code == 401


def test_confirm_password_reset_with_short_password(client):
    """Confirmar reset con password corto devuelve 422."""
    response = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "reset_token": "some.token",
            "new_password": "short",
        },
    )

    assert response.status_code == 422


def test_confirm_password_reset_requires_token(client):
    """Confirmar reset sin token devuelve 422."""
    response = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "reset_token": "",
            "new_password": "newpass123",
        },
    )

    assert response.status_code == 422


def test_password_reset_request_with_invalid_email(client):
    """Solicitud de reset con email invalido devuelve 422."""
    response = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "invalid-email"},
    )

    assert response.status_code == 422
