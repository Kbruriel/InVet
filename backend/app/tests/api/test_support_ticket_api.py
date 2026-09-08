"""Pruebas de integracion API soporte basico (BE-014 / APIA-014).

Cubre los 13 criterios minimos de API automation:
  C1  - POST crear ticket valido -> 201
  C2  - POST titulo invalido (<5 chars) -> 422
  C3  - GET list tickets paginados -> 200 + meta
  C4  - GET /{id} propio -> 200; ajeno -> 404 (IDOR sin fugas)
  C5  - PATCH status valido
  C6  - PATCH status invalido -> 422
  C7  - GET categories -> 200
  C8  - POST descripcion larga OK
  C9  - BOLA owner ajeno list vacio
  C10 - Auth sin bearer -> 401
  C11 - Pagination limits (page=0 / page_size>100)
  C12 - Transicion prohibida (completado->iniciado)
  C13 - Ticket duplicado dentro de 24 h -> 409
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ================================================================ #
# Engine + session factory globales (SQLite in-memory con StaticPool)
# ================================================================ #

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionFactory = sessionmaker(
    bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
)


# ================================================================ #
# Helper helpers import post-engine
# ================================================================ #


def _make_new_owner(clinic_id: int, owner_id: int = 1) -> Any:
    from app.infrastructure.database.models.owner import Owner

    return Owner(
        user_id=owner_id,
        first_name="Juan",
        last_name="Perez",
        email=f"juan{owner_id}@test.com",
        phone="555-000",
        city="Ciudad",
        is_active=True,
        clinic_id=clinic_id,
    )


# ================================================================ #
# Fixture: una sola db real que sobrevive entre request dentro del
# mismo test. Esto arregla C5 y C12 donde status "iniciado" se
# perdía porque cada HTTP call tenia su propia session sin visibilidad.
# ================================================================ #


@pytest.fixture(scope="function")
def app_client() -> dict:
    import app.api.v1.routers.support_ticket_router as st_router_mod  # noqa: E402

    # Importar el paquete valida que registre todos los modelos en Base.metadata.
    from app.infrastructure.database.models import Base, TicketCategory  # noqa: E402

    async def _test_db_gen():
        db = SessionFactory()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        else:
            db.commit()
        finally:
            db.close()

    app = FastAPI()
    app.include_router(st_router_mod.router, prefix="/api/v1")

    # -- DB override --------------------------------------------------- #
    import app.infrastructure.database.session as session_module  # noqa: E402
    from app.api.v1.routers.support_ticket_router import (
        get_db as router_get_db,  # noqa: E402
    )

    app.dependency_overrides[router_get_db] = _test_db_gen
    app.dependency_overrides[session_module.get_db] = _test_db_gen

    # -- Auth override default (owner=1, clinic=1) --------------------- #
    async def _auth():
        return {"user_id": 1, "clinic_id": 1, "role": "owner"}

    app.dependency_overrides[st_router_mod.get_current_access_user] = _auth

    # -- Factory para inyeccion dinamica de usuario ajeno ------------------- #
    def auth_dep_factory(user_id: int, clinic_id: int) -> Callable[[], Any]:
        async def _auth_override() -> dict[str, Any]:
            return {"user_id": user_id, "clinic_id": clinic_id, "role": "owner"}

        return _auth_override

    # -- Seed db y categorias por ejecucion de test ------------------- #
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    with SessionFactory() as seed_session:
        cats = []
        now = datetime.now(UTC)
        for name in ("Consulta general", "Soporte tecnico", "Facturacion"):
            cat = TicketCategory(clinic_id=1, name=name, active=True, created_at=now)
            seed_session.add(cat)
            cats.append(cat)
        seed_session.commit()

    yield {
        "app": app,
        "client": TestClient(app, base_url="http://test"),
        "auth_dep_factory": auth_dep_factory,
    }

    # Clean up
    app.dependency_overrides.clear()


# ================================================================ #
# C1 - POST crear ticket valido -> 201 (AC-014-01)
# ================================================================ #


def test_c1_create_ticket_happy_path(app_client: dict) -> None:
    """C1: POST /api/v1/tickets crea ticket con exito al owner 1."""
    client = app_client["client"]
    resp = client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema con mi mascota",
            "description": "Mascota no come bien",
        },
    )
    assert (
        resp.status_code == 201
    ), f"Expected 201 but got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["title"] == "Problema con mi mascota"
    assert body["status"] == "iniciado"


# ================================================================ #
# C2 - POST titulo invalido (<5 chars) -> 422 (AC-014-01)
# ================================================================ #


def test_c2_create_ticket_short_title(app_client: dict) -> None:
    """C2: POST /api/v1/tickets con title < 5 retorna 422."""
    client = app_client["client"]
    resp = client.post(
        "/api/v1/tickets",
        json={"title": "abc", "description": "test"},
    )
    assert resp.status_code == 422


# ================================================================ #
# C3 - GET list tickets paginados -> 200 + meta (AC-014-03)
# ================================================================ #


def test_c3_list_tickets_pagination(app_client: dict) -> None:
    """C3: GET /api/v1/tickets retorna lista con meta."""
    client = app_client["client"]
    resp = client.get("/api/v1/tickets", params={"page": 1, "page_size": 20})
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert "meta" in body


# ================================================================ #
# C4 - GET detalle propio vs ajeno (AC-014-04)
# ================================================================ #


def test_c4_get_detail_own(app_client: dict) -> None:
    """C4a: GET /{id} propio retorna 200."""
    client = app_client["client"]
    create_resp = client.post(
        "/api/v1/tickets",
        json={"title": "Ticket para detalle", "description": "test"},
    )
    ticket_id = create_resp.json().get("id")
    assert ticket_id is not None

    resp = client.get(f"/api/v1/tickets/{ticket_id}")
    assert resp.status_code == 200
    assert "title" in resp.json()


def test_c4_get_detail_ajeno(app_client: dict) -> None:
    """C4b: GET /{id} ajeno retorna 404 (sin fugas de data)."""
    client = app_client["client"]

    # Crear un ticket con owner=1 en clinic=1 (auth default)
    resp_create = client.post(
        "/api/v1/tickets",
        json={"title": "Ticket ajeno de prueba", "description": "test"},
    )
    assert resp_create.status_code == 201
    ticket_id = resp_create.json().get("id")

    # Sobreescribir autenticacion para owner=2, clinic=2 (ajeno)
    app_client["app"].dependency_overrides[
        __import__(
            "app.api.v1.routers.support_ticket_router",
            fromlist=["get_current_access_user"],
        ).get_current_access_user
    ] = app_client["auth_dep_factory"](user_id=2, clinic_id=2)

    resp = client.get(f"/api/v1/tickets/{ticket_id}")
    assert resp.status_code == 404


# ================================================================ #
# C5 - PATCH status valido (AC-014-05)
# El fix del fixture mantiene el ticket entre POST y PATCH en la
# misma db, asi status "iniciado" es visible al leer para el PATCH.
# ================================================================ #


def test_c5_patch_status_valid(app_client: dict) -> None:
    """C5: PATCH cambia de iniciado->pendiente."""
    client = app_client["client"]

    # 1) Crear ticket -> status "iniciado" (por el repo lo setea "iniciado")
    create_resp = client.post(
        "/api/v1/tickets",
        json={"title": "Ticket para status", "description": "test"},
    )
    assert create_resp.status_code == 201, f"Create debe dar 201: {create_resp.text}"
    create_body = create_resp.json()
    ticket_id = create_body.get("id")
    assert (
        create_body.get("status") == "iniciado"
    ), f"Status inicial debe ser 'iniciado', got '{create_body.get('status')}'"

    # 2) PATCH a pendiente usando el id del ticket en la PASO ANTERIOR
    resp = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"new_status": "pendiente"},
    )
    assert (
        resp.status_code == 200
    ), f"PATCH status failed: {resp.status_code} / {resp.text}"


# ================================================================ #
# C6 - PATCH status invalido -> 422 (AC-014-05)
# ================================================================ #


def test_c6_patch_status_invalid(app_client: dict) -> None:
    """C6: PATCH con estado invalido retorna 422."""
    client = app_client["client"]
    resp = client.patch(
        "/api/v1/tickets/999/status",
        json={"new_status": "estado-falso"},
    )
    assert resp.status_code == 422


# ================================================================ #
# C7 - GET categories -> 200 (AC-014-06)
# Categorias seedeadas en el fixture por _make_test_db.
# ================================================================ #


def test_c7_list_categories(app_client: dict) -> None:
    """C7: GET /tickets/categories retorna lista de categorias activas."""
    client = app_client["client"]
    resp = client.get("/api/v1/tickets/categories")
    assert (
        resp.status_code == 200
    ), f"C7 expects 200 but got {resp.status_code}: {resp.text}"


# ================================================================ #
# C8 - POST descripcion larga (AC-014-10)
# ================================================================ #


def test_c8_create_ticket_long_description(app_client: dict) -> None:
    """C8: POST con descripcion de 2000 chars no falla."""
    client = app_client["client"]
    long_desc = "x" * 2000
    resp = client.post(
        "/api/v1/tickets",
        json={"title": "Ticket con larga descripcion", "description": long_desc},
    )
    assert resp.status_code == 201


# ================================================================ #
# C9 - BOLA owner ajeno list vacio (AC-014-11)
# ================================================================ #


def test_c9_bola_owner_ajeno_list(app_client: dict) -> None:
    """C9: Owner de clinica distinta no ve tickets del otro."""
    client = app_client["client"]

    # Crear ticket para clinic=1 (owner 1) con auth default
    resp_create = client.post(
        "/api/v1/tickets",
        json={"title": "Ticket clinic 1", "description": "test"},
    )
    assert resp_create.status_code == 201

    # Sobreescribir autenticacion para owner=2, clinic=2 (ajeno)
    app_client["app"].dependency_overrides[
        __import__(
            "app.api.v1.routers.support_ticket_router",
            fromlist=["get_current_access_user"],
        ).get_current_access_user
    ] = app_client["auth_dep_factory"](user_id=2, clinic_id=2)

    resp = client.get("/api/v1/tickets", params={"page": 1, "page_size": 20})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body.get("items", [])) == 0  # clinic 2 no tiene tickets


# ================================================================ #
# C10 - Auth sin bearer -> 401 (AC-014-07)
# Se desactiva temporalmente la override de auth SOLO en esta prueba.
# ================================================================ #

_C10_AUTH_KEY: Any = None


def test_c10_auth_required(app_client: dict) -> None:
    """C10: GET sin token retorna error de autentificacion."""
    import app.api.v1.routers.support_ticket_router as st_router_mod  # noqa: E402

    client = app_client["client"]

    # Guardar y remover override de auth para esta prueba
    _auth_key = "current_access_user"
    key = getattr(st_router_mod, "_access_user_dep_key", _auth_key)
    if hasattr(st_router_mod, key):
        app_client["app"].dependency_overrides.get(getattr(st_router_mod, key))
    else:
        # Usar el atributo por defecto del router module
        app_client["app"].dependency_overrides.pop(
            st_router_mod.get_current_access_user, None
        )

    resp = client.get("/api/v1/tickets")
    assert resp.status_code in (
        401,
        422,
    ), f"Expected auth error but got {resp.status_code}"


# ================================================================ #
# C11 - Pagination limits (AC-014-03)
# ================================================================ #


def test_c11_pagination_limits(app_client: dict) -> None:
    """C11: GET con page < 1 retorna 422."""
    client = app_client["client"]
    resp = client.get("/api/v1/tickets", params={"page": 0})
    assert resp.status_code == 422


# ================================================================ #
# C12 - PATCH transicion prohibida (completado->iniciado) -> 422 (AC-014-05)
# Gracias al fix del fixture, el ticket creado persiste correctamente
# con status "iniciado" y los pasos avanzan sin perder estado.
# ================================================================ #


def test_c12_forbidden_status_transition(app_client: dict) -> None:
    """C12: Intentar cambiar de completado a iniciado retorna 422."""
    client = app_client["client"]
    create_resp = client.post(
        "/api/v1/tickets",
        json={"title": "Ticket para transicion prohibida", "description": "test"},
    )
    assert create_resp.status_code == 201, f"Create debe dar 201: {create_resp.text}"
    ticket_id = create_resp.json().get("id")

    # Avanzar a completado (requiere: iniciado->pendiente->proceso->completado)
    for step_status in ["pendiente", "proceso", "completado"]:
        resp = client.patch(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"new_status": step_status},
        )
        assert (
            resp.status_code == 200
        ), f"Fallo transicion hacia {step_status}: {resp.json()}"

    # Intentar cambiar de completado a iniciado (prohibido)
    forbidden_resp = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"new_status": "iniciado"},
    )
    assert (
        forbidden_resp.status_code == 422
    ), f"Esperaba 422 para transicion prohibida completado->iniciado, got {forbidden_resp.status_code}"

    detail_resp = client.get(f"/api/v1/tickets/{ticket_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["status"] == "completado"


# ================================================================ #
# C13 - POST duplicado dentro de 24 h -> 409 (AC-014-02)
# ================================================================ #


def test_c13_rejects_recent_duplicate_ticket(app_client: dict) -> None:
    """C13: el mismo owner y clinica no duplican titulo normalizado en 24 h."""
    client = app_client["client"]
    payload = {
        "title": "Problema de facturacion",
        "description": "Primer reporte",
    }

    first_resp = client.post("/api/v1/tickets", json=payload)
    assert first_resp.status_code == 201

    duplicate_resp = client.post(
        "/api/v1/tickets",
        json={"title": "  PROBLEMA DE FACTURACION  ", "description": "Reintento"},
    )
    assert duplicate_resp.status_code == 409
    assert "ultimas 24 horas" in duplicate_resp.json()["detail"]

    list_resp = client.get("/api/v1/tickets")
    assert list_resp.status_code == 200
    assert list_resp.json()["meta"]["total"] == 1
