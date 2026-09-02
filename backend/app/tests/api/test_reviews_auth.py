"""Tests de autenticacion para resenas (BE-012-T06 / QA-012).

Cubre el caso minimo "401 sin token" en cada endpoint autenticado de
resenas, siguiendo el patron de ``test_payments_auth.py`` (BE-011-T06):
se monta la app SIN override de ``get_current_access_user`` para que el
guarda OAuth de FastAPI devuelva 401 antes que la logica de negocio.

El listado publico (``GET /api/v1/reviews/public/{branch_id}``) es anonimo
por diseño y queda fuera de este modulo (cubierto en ``test_reviews_api.py``).
"""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import FastAPI

import app.api.v1.routers.review_router as review_router_mod

PAYLOAD_CREATE = {"appointment_id": 1, "rating": 5, "comment": "Ok"}
PAYLOAD_RESPOND = {"body": "Gracias por su feedback"}


def _unauthenticated_app() -> Iterator[dict[str, object]]:
    """App de resenas SIN override de autenticacion (401 en cada llamada)."""
    app = FastAPI()
    app.include_router(review_router_mod.router, prefix="/api/v1")

    mock_service = AsyncMock()
    mock_branch_repo = AsyncMock()
    mock_branch_repo.get_branch_by_id = AsyncMock(return_value=AsyncMock(id=1))

    app.dependency_overrides[review_router_mod.get_review_service] = (
        lambda: mock_service
    )
    app.dependency_overrides[review_router_mod.get_branch_repo] = (
        lambda: mock_branch_repo
    )

    client_factory = lambda: httpx.AsyncClient(  # noqa: E731
        transport=httpx.ASGITransport(app=app), base_url="http://t"
    )
    yield {"app": app, "client_factory": client_factory, "mock_service": mock_service}
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_reviews() -> Iterator[dict[str, object]]:
    yield from _unauthenticated_app()


class TestReviewsAuth:
    """401 sin token en cada endpoint autenticado de resenas."""

    @pytest.mark.asyncio
    async def test_create_without_token_returns_401(
        self, unauthenticated_reviews: dict[str, object]
    ) -> None:
        client_factory = unauthenticated_reviews["client_factory"]
        client = client_factory()
        async with client:
            resp = await client.post("/api/v1/reviews", json=PAYLOAD_CREATE)
        assert resp.status_code == 401
        assert resp.json()["detail"] in {
            "Not authenticated",
            "Could not validate credentials",
        }

    @pytest.mark.asyncio
    async def test_create_with_invalid_token_returns_401(
        self, unauthenticated_reviews: dict[str, object]
    ) -> None:
        client_factory = unauthenticated_reviews["client_factory"]
        client = client_factory()
        async with client:
            resp = await client.post(
                "/api/v1/reviews",
                json=PAYLOAD_CREATE,
                headers={"Authorization": "Bearer token-invalido"},
            )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Token inválido"

    @pytest.mark.asyncio
    async def test_detail_without_token_returns_401(
        self, unauthenticated_reviews: dict[str, object]
    ) -> None:
        client_factory = unauthenticated_reviews["client_factory"]
        client = client_factory()
        async with client:
            resp = await client.get("/api/v1/reviews/1")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_clinical_without_token_returns_401(
        self, unauthenticated_reviews: dict[str, object]
    ) -> None:
        client_factory = unauthenticated_reviews["client_factory"]
        client = client_factory()
        async with client:
            resp = await client.get("/api/v1/reviews")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_respond_without_token_returns_401(
        self, unauthenticated_reviews: dict[str, object]
    ) -> None:
        client_factory = unauthenticated_reviews["client_factory"]
        client = client_factory()
        async with client:
            resp = await client.post("/api/v1/reviews/1/respond", json=PAYLOAD_RESPOND)
        assert resp.status_code == 401
