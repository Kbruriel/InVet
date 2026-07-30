"""Unit tests for token and password helpers used in QA-001."""

from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.api.clinic_router import _decode_bearer_payload as decode_clinic_bearer_payload
from app.core.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    verify_token,
)


def test_password_hash_round_trip() -> None:
    password = "s3cret-pass"

    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-pass", hashed_password)


def test_create_and_verify_access_token_round_trip() -> None:
    token = create_access_token({"sub": "7"}, expires_delta=timedelta(minutes=5))

    payload = verify_token(token)

    assert payload["sub"] == "7"
    assert "exp" in payload


def test_verify_token_rejects_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token inválido"


def test_get_current_user_accepts_jwt_token() -> None:
    token = create_access_token({"sub": "9"})

    current_user = get_current_user(token=token)

    assert current_user == {"id": 9}


def test_get_current_user_rejects_token_without_subject() -> None:
    token = create_access_token({"scope": "read"})

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token=token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


def test_clinic_router_user_extractor_accepts_legacy_numeric_bearer() -> None:
    current_user = decode_clinic_bearer_payload("1")

    assert current_user == {}
