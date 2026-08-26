"""Tests de API para reseñas y respuestas clínicas (BE-012-T06).

Cubre los endpoints de reseñas:
- POST /api/v1/reviews — crear reseña (201 / 403 / 404 / 409 / 422).
- GET /api/v1/reviews/{id} — detalle autenticado (200 / 403 / 404).
- GET /api/v1/reviews/public/{branch_id} — listado público (200 / 404).
- GET /api/v1/reviews — listado clínico (200 / 403).
- POST /api/v1/reviews/{id}/respond — responder (200 / 403 / 404 / 409).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock

import pytest

import app.api.v1.routers.review_router as review_router_mod
from app.application.use_cases.review import (
    ReviewError,
    ReviewNotCompletedError,
    ReviewNotFoundError,
    ReviewRespondDuplicateError,
    ReviewRespondNotFoundError,
    ReviewDuplicateError,
)
from app.domain.entities.review import (
    Review,
    ReviewCreate,
    ReviewResponse,
)

CLINIC = 1


def _now() -> datetime:
    return datetime.now(UTC)


def _review(overrides=None) -> Review:
    data = dict(
        id=1,
        appointment_id=1,
        branch_id=1,
        clinic_id=CLINIC,
        user_id=50,
        rating=5,
        comment="Muy buena atención",
        created_at=_now(),
        updated_at=_now(),
    )
    if overrides:
        data.update(overrides)
    return Review(**data)


def _response(overrides=None) -> ReviewResponse:
    data = dict(
        id=100,
        review_id=1,
        branch_id=1,
        user_id=10,
        body="Gracias por su feedback",
        created_at=_now(),
        updated_at=_now(),
    )
    if overrides:
        data.update(overrides)
    return ReviewResponse(**data)





# ---------------------------------------------------------------------------
# POST /api/v1/reviews
# ---------------------------------------------------------------------------


class TestCreateReviewAPI:
    @pytest.mark.asyncio
    async def test_create_success_201(self, review_app):
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews",
                json={"appointment_id": 1, "rating": 5, "comment": "Ok"},
            )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["rating"] == 5
        assert body["appointment_id"] == 1
        review_app["mock_service"].create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_invalid_rating_422(self, review_app):
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews", json={"appointment_id": 1, "rating": 99}
            )
        assert resp.status_code == 422
        review_app["mock_service"].create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_appointment_not_completed_422(self, review_app):
        review_app["mock_service"].create = AsyncMock(
            side_effect=ReviewNotCompletedError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews", json={"appointment_id": 1, "rating": 4}
            )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_not_authorized_403(self, review_app):
        from app.application.use_cases.review import ReviewNotAuthorizedError

        review_app["mock_service"].create = AsyncMock(
            side_effect=ReviewNotAuthorizedError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews", json={"appointment_id": 1, "rating": 4}
            )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_create_duplicate_409(self, review_app):
        review_app["mock_service"].create = AsyncMock(
            side_effect=ReviewDuplicateError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews", json={"appointment_id": 1, "rating": 4}
            )
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# GET /api/v1/reviews/{id}
# ---------------------------------------------------------------------------


class TestGetReviewAPI:
    @pytest.mark.asyncio
    async def test_get_success_200(self, review_app):
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/1")
        assert resp.status_code == 200, resp.text
        assert resp.json()["id"] == 1
        review_app["mock_service"].get.assert_awaited_once_with(1, CLINIC)

    @pytest.mark.asyncio
    async def test_get_not_found_404(self, review_app):
        review_app["mock_service"].get = AsyncMock(
            side_effect=ReviewNotFoundError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/999")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_without_clinic_403(self, review_app):
        """Usuario sin clínica asociada → 403 en el router."""
        async def user_without_clinic() -> dict[str, Any]:
            return {"id": 100, "user_id": 100, "role": "owner"}

        review_app["app"].dependency_overrides[
            review_router_mod.get_current_access_user
        ] = user_without_clinic
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/1")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /api/v1/reviews/public/{branch_id}
# ---------------------------------------------------------------------------


class TestListPublicAPI:
    @pytest.mark.asyncio
    async def test_list_public_success_200(self, review_app):
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/public/1")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert len(body["items"]) == 2
        assert body["meta"]["total"] == 2
        assert body["meta"]["page"] == 1
        review_app["mock_service"].list_public.assert_awaited_once_with(
            branch_id=1, page=1, page_size=20
        )

    @pytest.mark.asyncio
    async def test_list_public_branch_not_found_404(self, review_app):
        review_app["mock_branch_repo"].get_branch_by_id = AsyncMock(
            return_value=None
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/public/999")
        assert resp.status_code == 404
        review_app["mock_service"].list_public.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_list_public_pagination_passed(self, review_app):
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get(
                "/api/v1/reviews/public/7",
                params={"page": 3, "page_size": 10},
            )
        assert resp.status_code == 200
        review_app["mock_service"].list_public.assert_awaited_once_with(
            branch_id=7, page=3, page_size=10
        )


# ---------------------------------------------------------------------------
# GET /api/v1/reviews (listado clínico)
# ---------------------------------------------------------------------------


class TestListClinicAPI:
    @pytest.mark.asyncio
    async def test_list_clinical_owner_forbidden_403(self, review_app):
        """El rol owner no puede listar (solo equipo clínico)."""
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews")
        assert resp.status_code == 403
        review_app["mock_service"].list_clinical.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_list_clinical_staff_success_200(self, review_app):
        async def staff_user() -> dict[str, Any]:
            return {"id": 10, "user_id": 10, "clinic_id": CLINIC, "role": "staff"}

        review_app["app"].dependency_overrides[
            review_router_mod.get_current_access_user
        ] = staff_user
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert len(body["items"]) == 1
        review_app["mock_service"].list_clinical.assert_awaited_once_with(
            clinic_id=CLINIC, branch_id=None, page=1, page_size=20
        )

    @pytest.mark.asyncio
    async def test_list_clinical_with_branch_filter(self, review_app):
        async def vet_user() -> dict[str, Any]:
            return {"id": 10, "user_id": 10, "clinic_id": CLINIC, "role": "veterinarian"}

        review_app["app"].dependency_overrides[
            review_router_mod.get_current_access_user
        ] = vet_user
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews", params={"branch_id": 2})
        assert resp.status_code == 200
        review_app["mock_service"].list_clinical.assert_awaited_once_with(
            clinic_id=CLINIC, branch_id=2, page=1, page_size=20
        )


# ---------------------------------------------------------------------------
# POST /api/v1/reviews/{id}/respond
# ---------------------------------------------------------------------------


class TestRespondReviewAPI:
    def _clinical_user(self, review_app, role: str = "veterinarian") -> None:
        async def clinical() -> dict[str, Any]:
            return {"id": 10, "user_id": 10, "clinic_id": CLINIC, "role": role}

        review_app["app"].dependency_overrides[
            review_router_mod.get_current_access_user
        ] = clinical

    @pytest.mark.asyncio
    async def test_respond_success_200(self, review_app):
        self._clinical_user(review_app)
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews/1/respond", json={"body": "Gracias"}
            )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["review_id"] == 1
        assert body["body"] == "Gracias por su feedback"
        review_app["mock_service"].respond.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_respond_owner_forbidden_403(self, review_app):
        """Rol owner no puede responder."""
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews/1/respond", json={"body": "Hola"}
            )
        assert resp.status_code == 403
        review_app["mock_service"].respond.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_respond_invalid_body_422(self, review_app):
        self._clinical_user(review_app)
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/reviews/1/respond", json={"body": ""})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_respond_missing_review_404(self, review_app):
        self._clinical_user(review_app)
        review_app["mock_service"].respond = AsyncMock(
            side_effect=ReviewRespondNotFoundError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews/999/respond", json={"body": "Hola"}
            )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_respond_already_answered_409(self, review_app):
        self._clinical_user(review_app)
        review_app["mock_service"].respond = AsyncMock(
            side_effect=ReviewRespondDuplicateError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews/1/respond", json={"body": "Hola"}
            )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_respond_service_error_propagated(self, review_app):
        self._clinical_user(review_app, role="staff")
        review_app["mock_service"].respond = AsyncMock(
            side_effect=ReviewError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews/1/respond", json={"body": "Hola"}
            )
        assert resp.status_code == 400
