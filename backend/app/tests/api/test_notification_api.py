"""Pruebas API de notificaciones internas (BE-013-T05).

Cubre:
- 200 listado propio con meta de paginacion.
- 200 GET detalle propio y 200 PATCH marcar-leida propia.
- 404 BOLA: detalle/marca de notificacion ajena (otro usuario/clinica).
- 403 usuario sin clinica asociada (listado, read-all, count).
- 401 dict de usuario sin identidad en cualquier endpoint.
- La emision HTTP ya no existe: POST /notifications/emit → 404/405.
- 200 read-all / count consistentes con el estado del repositorio REAL.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_current_access_user as auth_dep
from app.infrastructure.database import session as session_module
from app.infrastructure.database.models.base import Base
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.notification import (
    Notification as NotificationModel,
)
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.user import User as UserModel
from app.infrastructure.database.session import get_db


def _import_router() -> tuple:
    import app.api.v1.routers.notification_router as notif_router_mod

    return notif_router_mod, notif_router_mod.router


test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# Sobrescribir el engine global ANTES de importar la app/router.
session_module.engine = test_engine
session_module.SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)
TestingSessionLocal = session_module.SessionLocal


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()


def _override_auth(user_id: int | None, clinic_id: int | None):
    def auth() -> dict:
        if user_id is None:
            return {}
        data: dict = {"id": user_id, "user_id": user_id, "role": "staff"}
        if clinic_id is not None:
            data["clinic_id"] = clinic_id
            data["tenant_id"] = clinic_id
        return data

    return auth


@pytest.fixture()
def app_client() -> Iterator[TestClient]:
    notif_router_mod, notif_router = _import_router()
    app = FastAPI()
    app.include_router(notif_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = _override_get_db
    # Se sobreescribe en cada prueba con los IDs del seed.
    app.dependency_overrides[auth_dep] = _override_auth(1, 1)
    Base.metadata.create_all(bind=test_engine)
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def _seed() -> tuple[int, int, int, int, int, int, int]:
    """Crea 2 clinicas + 2 users + 2 owners y 3 notificaciones.

    Devuelve (u1, u2, c1, c2, n1_noLeida_u1, n2_leida_u1, n3_noLeida_u2).
    """
    with TestingSessionLocal() as db:
        c1 = ClinicModel(
            name="Clinica Uno",
            address="A1",
            city="C1",
            state="S1",
            country="MX",
            postal_code="010101",
        )
        c2 = ClinicModel(
            name="Clinica Dos",
            address="A2",
            city="C2",
            state="S2",
            country="MX",
            postal_code="020202",
        )
        db.add_all([c1, c2])
        db.flush()
        u1 = UserModel(
            email="u1@test.com",
            username="u1",
            hashed_password="x",
            first_name="Uno",
            last_name="User",
        )
        u2 = UserModel(
            email="u2@test.com",
            username="u2",
            hashed_password="x",
            first_name="Dos",
            last_name="User",
        )
        db.add_all([u1, u2])
        db.flush()
        o1 = OwnerModel(
            user_id=u1.id,
            first_name="Uno",
            last_name="Owner",
            email="o1@test.com",
            clinic_id=c1.id,
        )
        o2 = OwnerModel(
            user_id=u2.id,
            first_name="Dos",
            last_name="Owner",
            email="o2@test.com",
            clinic_id=c2.id,
        )
        db.add_all([o1, o2])

        n1 = NotificationModel(
            clinic_id=c1.id,
            user_id=u1.id,
            event_type="appointment_created",
            subject="Cita creada",
            body="cita/1",
            ref_type="appointment",
            ref_id=1,
            is_read=False,
        )
        n2 = NotificationModel(
            clinic_id=c1.id,
            user_id=u1.id,
            event_type="payment_received",
            subject="Pago recibido",
            body="pago/2",
            ref_type="payment",
            ref_id=2,
            is_read=True,
        )
        n3 = NotificationModel(
            clinic_id=c2.id,
            user_id=u2.id,
            event_type="appointment_created",
            subject="Cita creada",
            body="cita/3",
            ref_type="appointment",
            ref_id=1,
            is_read=False,
        )
        db.add_all([n1, n2, n3])
        db.commit()
        ids = (u1.id, u2.id, c1.id, c2.id, n1.id, n2.id, n3.id)
        db.refresh(n1)
        db.refresh(n2)
        db.refresh(n3)
    return ids


def _as_user(app_client: TestClient, user_id: int, clinic_id: int) -> None:
    app_client.app.dependency_overrides[auth_dep] = _override_auth(user_id, clinic_id)


def _as_user_no_clinic(app_client: TestClient, user_id: int) -> None:
    app_client.app.dependency_overrides[auth_dep] = _override_auth(user_id, None)


def _as_anonymous(app_client: TestClient) -> None:
    app_client.app.dependency_overrides[auth_dep] = _override_auth(None, None)


class TestNotificationsAPI:
    def test_list_own_returns_metadata(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, _n1, _n2, _n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get("/api/v1/notifications")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["meta"]["total"] == 2
        assert body["meta"]["page"] == 1
        assert body["meta"]["page_size"] == 20
        assert len(body["items"]) == 2

    def test_list_unread_only_filters(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, _n1, _n2, _n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get("/api/v1/notifications", params={"unread_only": True})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["meta"]["total"] == 1
        assert all(it["is_read"] is False for it in body["items"])

    def test_pagination(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, _n1, _n2, _n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get(
            "/api/v1/notifications", params={"page": 1, "page_size": 1}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["meta"]["total"] == 2
        assert body["meta"]["pages"] == 2
        assert len(body["items"]) == 1

    def test_pagination_invalid_params_422(self, app_client: TestClient) -> None:
        """Validacion de query params fuera de bounds (FastAPI/Query)."""
        _seed()
        # page_size por encima del maximo (100)
        assert (
            app_client.get(
                "/api/v1/notifications", params={"page_size": 101}
            ).status_code
            == 422
        )
        # page_size por debajo del minimo (1)
        assert (
            app_client.get("/api/v1/notifications", params={"page_size": 0}).status_code
            == 422
        )
        # page por debajo del minimo (1)
        assert (
            app_client.get("/api/v1/notifications", params={"page": 0}).status_code
            == 422
        )
        # tipo invalido
        assert (
            app_client.get("/api/v1/notifications", params={"page": "abc"}).status_code
            == 422
        )

    def test_get_detail_own(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, n1, _n2, _n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get(f"/api/v1/notifications/{n1}")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["id"] == n1
        assert body["is_read"] is False
        assert body["ref_type"] == "appointment"

    def test_patch_mark_read_own(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, n1, _n2, _n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.patch(f"/api/v1/notifications/{n1}")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["is_read"] is True
        # read_at poblada (alias de serializacion readAt)
        assert body["readAt"] is not None

    def test_mark_read_idempotent(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, _n1, _n2, _n3 = _seed()
        _as_user(app_client, u1, c1)
        first = app_client.patch(f"/api/v1/notifications/{_n2}")
        assert first.status_code == 200
        second = app_client.patch(f"/api/v1/notifications/{_n2}")
        assert second.status_code == 200
        assert second.json()["is_read"] is True

    def test_get_detail_foreign_returns_404_bola(self, app_client: TestClient) -> None:
        """Un usuario de la clinica 1 no ve la notificacion del user/clinica 2 (BOLA)."""
        u1, _u2, c1, _c2, _n1, _n2, n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get(f"/api/v1/notifications/{n3}")
        assert resp.status_code == 404
        # Tampoco puede marcar-la como leida (IDOR de escritura)
        resp2 = app_client.patch(f"/api/v1/notifications/{n3}")
        assert resp2.status_code == 404
        # La notificacion ajena sigue sin estar leida
        with TestingSessionLocal() as db:
            state = db.get(NotificationModel, n3)
            assert state.is_read is False

    def test_list_scoped_by_tenant_excludes_other_clinics(
        self, app_client: TestClient
    ) -> None:
        u1, _u2, c1, _c2, n1, n2, n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get("/api/v1/notifications", params={"page_size": 100})
        assert resp.status_code == 200
        ids_seen = [it["id"] for it in resp.json()["items"]]
        assert n3 not in ids_seen
        assert n1 in ids_seen
        assert n2 in ids_seen

    def test_read_all_marks_only_unread_own(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, _n1, _n2, n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.post("/api/v1/notifications/read-all")
        assert resp.status_code == 200
        # Solo la no leida (n1); n2 ya estaba leida
        assert resp.json()["read"] == 1
        with TestingSessionLocal() as db:
            db.expire_all()
            state_foreign = db.get(NotificationModel, n3)
            assert state_foreign.is_read is False

    def test_count_unread_own_only(self, app_client: TestClient) -> None:
        u1, _u2, c1, _c2, _n1, _n2, n3 = _seed()
        _as_user(app_client, u1, c1)
        resp = app_client.get("/api/v1/notifications/count/unread")
        assert resp.status_code == 200
        assert resp.json()["unread"] == 1


class TestNotificationsSecurity:
    def test_user_without_clinic_list_403(self, app_client: TestClient) -> None:
        _seed()
        _as_user_no_clinic(app_client, 999)
        resp = app_client.get("/api/v1/notifications")
        assert resp.status_code == 403
        # El detail en prosa es "El usuario no tiene una clínica asociada."
        detail = resp.json()["detail"].lower()
        assert "usuario" in detail and "asociada" in detail

    def test_user_without_clinic_read_all_403(self, app_client: TestClient) -> None:
        _seed()
        _as_user_no_clinic(app_client, 999)
        resp = app_client.post("/api/v1/notifications/read-all")
        assert resp.status_code == 403

    def test_user_without_clinic_count_403(self, app_client: TestClient) -> None:
        _seed()
        _as_user_no_clinic(app_client, 999)
        resp = app_client.get("/api/v1/notifications/count/unread")
        assert resp.status_code == 403

    def test_anonymous_list_401(self, app_client: TestClient) -> None:
        _seed()
        _as_anonymous(app_client)
        resp = app_client.get("/api/v1/notifications")
        assert resp.status_code == 401

    def test_anonymous_read_all_401(self, app_client: TestClient) -> None:
        _seed()
        _as_anonymous(app_client)
        resp = app_client.post("/api/v1/notifications/read-all")
        assert resp.status_code == 401

    def test_anonymous_count_401(self, app_client: TestClient) -> None:
        _seed()
        _as_anonymous(app_client)
        resp = app_client.get("/api/v1/notifications/count/unread")
        assert resp.status_code == 401

    def test_anonymous_detail_401(self, app_client: TestClient) -> None:
        _seed()
        _as_anonymous(app_client)
        resp = app_client.get("/api/v1/notifications/1")
        assert resp.status_code == 401

    def test_emit_endpoint_removed(self, app_client: TestClient) -> None:
        """POST /notifications/emit (vector IDOR) ya no existe en surface HTTP."""
        _seed()
        resp = app_client.post(
            "/api/v1/notifications/emit",
            json={
                "user_id": 1,
                "clinic_id": 1,
                "event_type": "x",
                "ref_type": "x",
            },
        )
        assert resp.status_code in (404, 405)
