"""Pruebas unitarias directas para primitivas de seguridad."""

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_access_user,
    get_password_hash,
    verify_access_token,
    verify_password,
    verify_token,
)


def test_password_hash_roundtrip() -> None:
    password = "secret123"

    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_contains_access_claims() -> None:
    token = create_access_token(
        {"sub": "42", "email": "ada@example.com", "role": "admin"},
        expires_delta=timedelta(minutes=5),
    )

    payload = verify_token(token)

    assert payload["sub"] == "42"
    assert payload["email"] == "ada@example.com"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert verify_access_token(token)["type"] == "access"
    assert get_current_access_user(token)["id"] == 42


def test_refresh_token_is_not_accepted_as_access_token() -> None:
    token = create_refresh_token(
        {"sub": "42", "email": "ada@example.com"},
        expires_delta=timedelta(days=1),
    )

    payload = verify_token(token)

    assert payload["type"] == "refresh"
    with pytest.raises(HTTPException) as excinfo:
        verify_access_token(token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token inválido"
