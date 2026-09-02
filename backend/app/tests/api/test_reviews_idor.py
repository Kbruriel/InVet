"""Tests de IDOR/BOLA para resenas (BE-012-T06 / QA-012).

Cubre los casos minimos de seguridad del slice de resenas:
- 403 para rol propietario al responder una reseña (rol sin permiso).
- 403 para rol propietario al listar el listado clínico (solo equipo clínico).
- 404 BOLA: personal clínico de OTRA clínica no ve la reseña ajena (detalle).
- 403 BOLA: usuario sin clínica asociada no puede leer detalle/listado.
- 403 ownership: el cliente titular no es el propietario de la cita (crear).
- El listado clínico filtra EXCLUSIVAMENTE por el tenant del usuario.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.application.use_cases.review import (
    ReviewNotAuthorizedError,
    ReviewNotFoundError,
)

CLINIC = 1
OTHER_CLINIC = 99


def _as_user(review_app: dict, role: str, clinic_id: int | None) -> None:
    import app.api.v1.routers.review_router as review_router_mod

    async def user() -> dict[str, Any]:
        return {"id": 7, "user_id": 7, "clinic_id": clinic_id, "role": role}

    review_app["app"].dependency_overrides[
        review_router_mod.get_current_access_user
    ] = user


def _scoped_get(review_app: dict, review, tenant_id: int) -> None:
    """Servicio que solo expone la reseña a su tenant (BOLA simulada)."""

    async def get(review_id: int, clinic_id: int):
        if clinic_id != tenant_id:
            raise ReviewNotFoundError()
        return review

    review_app["mock_service"].get = get


class TestReviewsIDOR:
    """Permisos por rol y aislamiento de tenant en resenas."""

    # --- 403 rol ------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_owner_cannot_respond_returns_403(self, review_app: dict) -> None:
        """El propietario no puede responder una reseña (rol bloqueado)."""
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post("/api/v1/reviews/1/respond", json={"body": "Hola"})
        assert resp.status_code == 403
        review_app["mock_service"].respond.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_owner_cannot_list_clinical_returns_403(
        self, review_app: dict
    ) -> None:
        """El propietario no puede listar el listado clínico (rol bloqueado)."""
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews")
        assert resp.status_code == 403
        review_app["mock_service"].list_clinical.assert_not_awaited()

    # --- 404 BOLA cross-clinic ----------------------------------------------
    @pytest.mark.asyncio
    async def test_other_clinic_detail_returns_404(self, review_app: dict) -> None:
        """Veterinario de la clínica 1 no ve la reseña de la clínica 99 (BOLA)."""
        review = review_app["mock_service"].get.return_value
        _as_user(review_app, "veterinarian", OTHER_CLINIC)
        _scoped_get(review_app, review, tenant_id=CLINIC)
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/1")
        assert resp.status_code == 404

    # --- 403 usuario sin clínica asociada -----------------------------------
    @pytest.mark.asyncio
    async def test_user_without_clinic_get_detail_403(self, review_app: dict) -> None:
        """Un usuario sin clínica no puede leer el detalle de una reseña."""
        _as_user(review_app, "veterinarian", None)
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews/1")
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_user_without_clinic_list_clinical_403(
        self, review_app: dict
    ) -> None:
        """Un usuario sin clínica no puede listar el listado clínico (BOLA)."""
        _as_user(review_app, "veterinarian", None)
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews")
        assert resp.status_code == 403
        review_app["mock_service"].list_clinical.assert_not_awaited()

    # --- 403 ownership en crear ------------------------------------------------
    @pytest.mark.asyncio
    async def test_client_cannot_review_foreign_appointment_403(
        self, review_app: dict
    ) -> None:
        """El cliente no es el titular de la cita (ownership) → 403."""
        from unittest.mock import AsyncMock

        review_app["mock_service"].create = AsyncMock(
            side_effect=ReviewNotAuthorizedError()
        )
        client = review_app["client_factory"]()
        async with client:
            resp = await client.post(
                "/api/v1/reviews",
                json={"appointment_id": 1, "rating": 5, "comment": "Ok"},
            )
        assert resp.status_code == 403

    # --- filtro de tenant en listado ----------------------------------------
    @pytest.mark.asyncio
    async def test_list_clinical_scoped_to_user_tenant(self, review_app: dict) -> None:
        """El listado clínico usa SOLO el tenant del usuario autenticado."""
        _as_user(review_app, "staff", CLINIC)
        captured: dict[str, Any] = {}

        async def list_clinical(**kwargs):
            captured.update(kwargs)
            return ([], 0)

        review_app["mock_service"].list_clinical = list_clinical
        client = review_app["client_factory"]()
        async with client:
            resp = await client.get("/api/v1/reviews")
        assert resp.status_code == 200, resp.text
        assert captured["clinic_id"] == CLINIC
        assert captured["branch_id"] is None
        assert captured["page"] == 1
        assert captured["page_size"] == 20
