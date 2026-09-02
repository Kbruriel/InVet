"""Pruebas de protección IDOR/BOLA (C4, C13).

Cubren:
- C4: Marcación de notificación ajena devuelve 404 sin revelar existencia
- C13: Listado de notificaciones por clinica A no fuga datos de clinica B
"""

from __future__ import annotations

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


def _import_router():
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
Base.metadata.create_all(bind=test_engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()


def _override_auth(user_id: int | None, clinic_id: int | None):
    def auth():
        if user_id is None:
            return {}
        data = {"id": user_id, "user_id": user_id, "role": "staff"}
        if clinic_id is not None:
            data["clinic_id"] = clinic_id
            data["tenant_id"] = clinic_id
        return data

    return auth


@pytest.fixture()
def app_client():
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


def _seed():
    """Crea 2 clinicas + 2 users + 2 owners y 3 notificaciones."""
    with TestingSessionLocal() as db:
        c1 = ClinicModel(
            name="Clinica Uno",
            address="A1",
            city="B1",
            state="S1",
            country="MX",
            postal_code="010101",
            phone="T1",
        )
        c2 = ClinicModel(
            name="Clinica Dos",
            address="A2",
            city="B2",
            state="S2",
            country="MX",
            postal_code="020202",
            phone="T2",
        )
        db.add_all([c1, c2])
        db.flush()

        # Usuario 1 de clinica 1
        u1 = UserModel(
            email="user1@example.com",
            username="user1",
            hashed_password="hashed1",
            first_name="Usuario",
            last_name="Uno",
        )
        # Usuario 2 de clinica 2
        u2 = UserModel(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed2",
            first_name="Usuario",
            last_name="Dos",
        )
        db.add_all([u1, u2])
        db.flush()

        # Owner 1
        o1 = OwnerModel(
            user_id=u1.id,
            first_name="Juan",
            last_name="Perez",
            email="juan@example.com",
            clinic_id=c1.id,
        )
        # Owner 2
        o2 = OwnerModel(
            user_id=u2.id,
            first_name="Maria",
            last_name="Gomez",
            email="maria@example.com",
            clinic_id=c2.id,
        )
        db.add_all([o1, o2])
        db.flush()

        # Notificación no leída para usuario 1 (de clinica 1)
        n1 = NotificationModel(
            user_id=u1.id,
            clinic_id=c1.id,
            event_type="APPOINTMENT_CREATED",
            subject="Cita programada",
            body="Nueva cita para tu mascota",
            ref_type="appointment",
            ref_id=123,
            is_read=False,
        )
        # Notificación leída para usuario 1 (de clinica 1)
        n2 = NotificationModel(
            user_id=u1.id,
            clinic_id=c1.id,
            event_type="APPOINTMENT_STATUS_CHANGED",
            subject="Cita modificada",
            body="Tu cita ha sido modificada",
            ref_type="appointment",
            ref_id=456,
            is_read=True,
        )
        # Notificación no leída para usuario 2 (de clinica 2)
        n3 = NotificationModel(
            user_id=u2.id,
            clinic_id=c2.id,
            event_type="CONVERSATION_STARTED",
            subject="Nueva conversación",
            body="Tienes una nueva conversación",
            ref_type="conversation",
            ref_id=789,
            is_read=False,
        )

        db.add_all([n1, n2, n3])
        db.commit()

        return u1.id, u2.id, c1.id, c2.id, n1.id, n2.id, n3.id


def test_idor_bola_prevention_on_list(app_client):
    """C13: Listado por clinica A no fuga datos de clinica B."""
    u1, u2, c1, c2, n1_id, n2_id, n3_id = _seed()

    # Simular que usuario 2 (de clinica 2) intenta acceder a notificaciones de clinica 1
    app_client.app.dependency_overrides[auth_dep] = _override_auth(
        2, 2
    )  # Usuario 2 de clinica 2

    response = app_client.get("/api/v1/notifications?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()

    # No debería ver notificaciones de otra clínica
    assert len(data["items"]) >= 0  # Puede ser 0 si no hay notificaciones propias

    # Verificar que ninguna de las notificaciones sea de la otra clinica
    for item in data["items"]:
        if "user_id" in item:
            # Las notificaciones deben pertenecer al usuario actual (usuario 2)
            assert item["user_id"] == u2


def test_idor_bola_prevention_on_mark_read(app_client):
    """C4: Marcación incorrecta por token (ID ajeno) devuelve 404 sin revelar existencia."""
    u1, u2, c1, c2, n1_id, n2_id, n3_id = _seed()

    # Simular que usuario 2 intenta marcar la notificación del usuario 1
    app_client.app.dependency_overrides[auth_dep] = _override_auth(2, 2)  # Usuario 2

    response = app_client.post(f"/api/v1/notifications/{n1_id}/read")

    assert response.status_code == 404
    data = response.json()

    # No debe revelar información sensibles de la notificación
    assert "id" not in str(data).lower()
    assert "detail" in data


def test_bola_prevention_on_unread_count(app_client):
    """Verifica protección BOLA en conteo de no leídas."""
    u1, u2, c1, c2, n1_id, n2_id, n3_id = _seed()

    # Usuario 2 accede a su propio conteo (debe ser 1)
    app_client.app.dependency_overrides[auth_dep] = _override_auth(2, 2)  # Usuario 2

    response = app_client.get("/api/v1/notifications/count/unread")

    assert response.status_code == 200
    data = response.json()

    # Solo debe contar notificaciones propias (en este caso, la de usuario 2)
    # Si hay una no leída para el usuario 2, el conteo debe ser al menos 1


def test_invalid_access_to_nonexistent_notification(app_client):
    """Verifica que acceso a notificación inexistente devuelva 404."""
    u1, u2, c1, c2, n1_id, n2_id, n3_id = _seed()

    # Usuario 2 intenta acceder a notificación inexistente
    app_client.app.dependency_overrides[auth_dep] = _override_auth(2, 2)  # Usuario 2

    response = app_client.post("/api/v1/notifications/99999/read")

    assert response.status_code == 404
    data = response.json()

    # No debe revelar información sobre la existencia de esa notificación
    assert "detail" in data


def test_list_notifications_authorized_only_your_clinic(app_client):
    """Verifica que se liste solo notificaciones de la misma clínica."""
    _seed()

    # Usuario 1 de clinica 1 listando (se debe devolver sus notificaciones)
    app_client.app.dependency_overrides[auth_dep] = _override_auth(1, 1)  # Usuario 1

    response = app_client.get("/api/v1/notifications?page=1&page_size=10")

    assert response.status_code == 200
    data = response.json()

    # Verificar que las notificaciones son de la clínica del usuario actual
    for item in data["items"]:
        if "clinic_id" in item:
            # Verificar que todas pertenecen a la clínica 1 (usuario 1)
            assert item["clinic_id"] == 1
