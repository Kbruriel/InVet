"""Tests de seguridad: autenticacion de reportes (BE-015-T09, AC-015-09/11).

Verifica el comportamiento del ``reports_router`` frente a la capa real de
autenticacion (``get_current_access_user``):

- sin token -> 401 Unauthorized
- token invalido (firmado con clave distinta) -> 401
- token expirado -> 401

La sesion de datos se sobreescribe por un objeto inerte (no es ``Session`` de
SQLAlchemy, por lo que ``get_current_access_user`` omite la consulta de
usuario y resuelve la identidad/clínica directamente del payload JWT, que es
exactamente lo que se quiere auditar: la decisión de acceso depende del token).

Validacion:
    python -m pytest backend/app/tests/integration/test_reports_auth.py -q
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.reports_router as reports_mod
import app.core.security as security_mod
from app.core.security import create_access_token


def _fake_db() -> Iterator[Any]:
    class _Fake:
        def close(self) -> None:
            pass

    yield _Fake()


@pytest.fixture
def auth_app() -> Iterator[FastAPI]:
    app = FastAPI()
    app.include_router(reports_mod.router, prefix="/api/v1/reports")
    # La autenticacion (get_current_access_user) usa app.core.security.get_db;
    # sobreescribimos esa sesion para que NO consulte la DB de usuarios y la
    # identidad/clinica se resuelva SOLO desde el payload JWT.
    app.dependency_overrides[security_mod.get_db] = _fake_db
    app.dependency_overrides[reports_mod._db] = _fake_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client_factory(auth_app: FastAPI):
    def _make() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=httpx.ASGITransport(app=auth_app),
            base_url="http://test",
        )

    return _make


def _valid_token(clinic_id: int = 1) -> str:
    return create_access_token(
        {"sub": "101", "clinic_id": clinic_id, "role": "veterinarian"}
    )


class TestReportsAuth:
    @pytest.mark.asyncio
    async def test_no_token_401(self, client_factory) -> None:
        client = client_factory()
        async with client:
            resp = await client.get("/api/v1/reports/appointments")

        # OAuth2PasswordBearer -> 401 con WWW-Authenticate cuando no hay token.
        assert resp.status_code == 401, resp.text
        assert resp.headers.get("WWW-Authenticate") is not None

    @pytest.mark.asyncio
    async def test_invalid_token_401(self, client_factory) -> None:
        # Token firmado con una clave distinta a SECRET_KEY -> firma invalida.
        from app.core.security import _require_secret_key

        bad_secret = "x" * max(16, len(_require_secret_key()) + 1)
        import jose  # type: ignore[import-untyped]

        bad_token = jose.jwt.encode(
            {"sub": "101", "clinic_id": 1, "type": "access"},
            bad_secret,
            algorithm="HS256",
        )

        client = client_factory()
        async with client:
            resp = await client.get(
                "/api/v1/reports/appointments",
                headers={"Authorization": f"Bearer {bad_token}"},
            )

        assert resp.status_code == 401, resp.text
        assert resp.json()["detail"] == "Token inválido"

    @pytest.mark.asyncio
    async def test_expired_token_401(self, client_factory) -> None:
        expired = create_access_token(
            {"sub": "101", "clinic_id": 1, "role": "veterinarian"},
            expires_delta=timedelta(days=-1),
        )

        client = client_factory()
        async with client:
            resp = await client.get(
                "/api/v1/reports/appointments",
                headers={"Authorization": f"Bearer {expired}"},
            )

        assert resp.status_code == 401, resp.text
        assert resp.json()["detail"] == "Token inválido"

    @pytest.mark.asyncio
    async def test_valid_token_passes_auth(self, client_factory) -> None:
        """Con token válido la autenticacion no bloquea (delega en el use-case)."""
        from app.api.v1.schemas.report_schemas import PaginatedResponse

        with patch.object(
            reports_mod,
            "uc_appointments",
            return_value=PaginatedResponse(items=[], total=0, page=1, size=20),
        ):
            client = client_factory()
            async with client:
                resp = await client.get(
                    "/api/v1/reports/appointments",
                    headers={"Authorization": f"Bearer {_valid_token()}"},
                )

        assert resp.status_code == 200, resp.text
