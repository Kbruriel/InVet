"""Pruebas de deduplicación de notificaciones (C8).

Cubren behavior funcional a nivel **servicio** y **repo**, no solo esquema:

- `NotificationService.emit()` consulta la clave de dedup en el repo antes
  de insertar → segundo call con misma clave retorna ``{"created": False, …}``
- `NotificationRepository.create_if_unique()` también filtra duplicadas a nivel
  ORM/DB como segundo resguardo.
- Combinaciones distintas (diferente ``ref_id`` o **user_id**) no activan dedup.
"""

from __future__ import annotations

import pytest

from app.application.notification_use_cases import NotificationService
from app.data.notification_repo import get_notification_repo
from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.owner import Owner
from app.infrastructure.database.models.user import User

# --------------------------------------------------------------------------- #
#  Helpers                                                                   #
# --------------------------------------------------------------------------- #


async def _create_base(db_session):
    """Seed mínimo de clinica / usuario para que el repo y servicio funcionen."""
    clinic = Clinic(
        name="Clinica Test-C8",
        address="A-test",
        city="B-test",
        state="S-test",
        country="MX",
        postal_code="070001",
        phone="555-TEST",
    )
    db_session.add(clinic)
    db_session.flush()

    user = User(
        email="c8user@example.com",
        username=f"c8user_{clinic.id}",
        hashed_password="pw-test",
        first_name="Usuario",
        last_name="C8",
    )
    db_session.add(user)
    db_session.flush()

    owner = Owner(
        user_id=user.id,
        first_name="Juan",
        last_name="Perez",
        email=f"juan.c8{clinic.id}@example.com",
        clinic_id=clinic.id,
    )
    db_session.add(owner)
    db_session.commit()

    return user.id, clinic.id


async def _make_service(db_session):
    """Fixture helper: repo + service listos."""
    repo = get_notification_repo(db_session)
    svc = NotificationService(repo)
    return svc


# --------------------------------------------------------------------------- #
#  C8 tests                                                                  #
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_emit_service_dedup_at_service_layer(db_session):
    """C8 (service): emit() dos veces con misma clave → el segundo call retorna already_exists sin insertar."""
    user_id, clinic_id = await _create_base(db_session)
    svc = await _make_service(db_session)

    # Primera emisión -> crea
    result_one = await svc.emit(
        user_id=user_id,
        clinic_id=clinic_id,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=101,
    )
    assert result_one["created"] is True

    # Segunda emisión con la misma clave dedup -> ya existe en repo
    result_dup = await svc.emit(
        user_id=user_id,
        clinic_id=clinic_id,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=101,
    )
    assert result_dup["created"] is False
    assert result_dup["reason"] == "already_exists"

    # Verificar que el repo no creó ninguna fila extra por resguardo interno
    count = await svc.repo.count_unread(user_id, clinic_id)
    assert count == 1, "no debe existir segunda fila en la BD"


@pytest.mark.asyncio
async def test_repo_create_if_unique_returns_none_on_dup(db_session):
    """C8 (repo): create_if_unique() directa -> segunda llamada retorna None."""
    user_id, clinic_id = await _create_base(db_session)
    repo = get_notification_repo(db_session)

    first = await repo.create_if_unique(
        clinic_id=clinic_id,
        user_id=user_id,
        event_type="appointment_created",
        subject="Primer evento",
        body="appointment/102 - primer",
        ref_type="appointment",
        ref_id=102,
    )
    assert first is not None

    dup = await repo.create_if_unique(
        clinic_id=clinic_id,
        user_id=user_id,
        event_type="appointment_created",
        subject="Duplicado en capa de datos",
        body="appointment/102 - dup",
        ref_type="appointment",
        ref_id=102,
    )
    assert dup is None

    # Verificar persistencia sin duplicación
    total = await repo.count_unread(user_id, clinic_id)
    assert total == 1


@pytest.mark.asyncio
async def test_same_event_different_ref_allowed_service(db_session):
    """C8 (service): mismo tipo de evento + diferente ref_id -> dos notificaciones."""
    user_id, clinic_id = await _create_base(db_session)
    svc = await _make_service(db_session)

    r1 = await svc.emit(
        user_id=user_id,
        clinic_id=clinic_id,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=201,
    )
    assert r1["created"] is True

    r2 = await svc.emit(
        user_id=user_id,
        clinic_id=clinic_id,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=202,  # diferente -> no dedup
    )
    assert r2["created"] is True

    count = await svc.repo.count_unread(user_id, clinic_id)
    assert count == 2


@pytest.mark.asyncio
async def test_same_event_different_ref_allowed_repo(db_session):
    """C8 (repo): misma combinación excepto ref_id -> ambas insertadas."""
    user_id, clinic_id = await _create_base(db_session)
    repo = get_notification_repo(db_session)

    n1 = await repo.create_if_unique(
        clinic_id=clinic_id,
        user_id=user_id,
        event_type="appointment_created",
        subject="Evento A",
        body="appointment/301 - ref A",
        ref_type="appointment",
        ref_id=301,
    )
    assert n1 is not None

    n2 = await repo.create_if_unique(
        clinic_id=clinic_id,
        user_id=user_id,
        event_type="appointment_created",
        subject="Evento B",
        body="appointment/302 - ref B",
        ref_type="appointment",
        ref_id=302,
    )
    assert n2 is not None

    items, total = await repo.list_by_user(user_id, clinic_id)
    assert total == 2


@pytest.mark.asyncio
async def test_different_owner_same_event_repo(db_session):
    """C8 (repo): el dedup es por usuario -> mismo ref pero otro user crea fila nueva."""
    # Crear base para usuario A
    uA, clinic_id = await _create_base(db_session)

    repo = get_notification_repo(db_session)
    n_a = await repo.create_if_unique(
        clinic_id=clinic_id,
        user_id=uA,
        event_type="appointment_created",
        subject="Evento para A",
        body="appointment/401 - ref para A",
        ref_type="appointment",
        ref_id=401,
    )
    assert n_a is not None

    # Crear base para usuario B (otro user)
    clinic_b = Clinic(
        name="Clinica Test-C8B",
        address="A-test-B",
        city="B-test-B",
        state="S-test-B",
        country="MX",
        postal_code="070002",
        phone="555-TESTB",
    )
    db_session.add(clinic_b)
    db_session.flush()

    uB = User(
        email="c8user-b@example.com",
        username=f"c8user_b_{clinic_b.id}",
        hashed_password="pw-test-b",
        first_name="Usuario",
        last_name="C8B",
    )
    db_session.add(uB)
    db_session.flush()

    # Misma ref_id pero diferente user -> no debe activar dedup
    n_b = await repo.create_if_unique(
        clinic_id=clinic_b.id,
        user_id=uB.id,
        event_type="appointment_created",
        subject="Evento para B (misma ref)",
        body="appointment/401 - ref para B",
        ref_type="appointment",
        ref_id=401,  # misma clave de referencia, diferente receptor
    )

    assert n_b is not None

    countA = await repo.count_unread(uA, clinic_id)
    countB = await repo.count_unread(uB.id, clinic_b.id)
    assert countA == 1 and countB == 1


@pytest.mark.asyncio
async def test_emit_service_dedup_different_user_same_ref(db_session):
    """C8 (service): diferentes usuarios con mismo ref_id no activan dedup."""
    userA, clinicA = await _create_base(db_session)

    svc_a = await _make_service(db_session)

    r1 = await svc_a.emit(
        user_id=userA,
        clinic_id=clinicA,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=500,
    )
    assert r1["created"] is True

    # Crear segunda base para usuario B con mismo ref_id
    clinic_b = Clinic(
        name="Clinica Test-C8-DiffUserB",
        address="A-test-BU",
        city="B-test-BU",
        state="S-test-BU",
        country="MX",
        postal_code="070003",
        phone="555-TESTBU",
    )
    db_session.add(clinic_b)
    db_session.flush()

    user_b = User(
        email="c8user-duB@example.com",
        username=f"c8dupb_{clinic_b.id}",
        hashed_password="pw-dup-B",
        first_name="UsuarioB",
        last_name="C8DupU",
    )
    db_session.add(user_b)
    db_session.flush()

    svc_b = NotificationService(get_notification_repo(db_session))
    r2 = await svc_b.emit(
        user_id=user_b.id,
        clinic_id=clinic_b.id,
        event_type="appointment_created",
        ref_type="appointment",
        ref_id=500,  # misma referencia pero receptor diferente
    )

    assert r2["created"] is True
    count_b = await svc_b.repo.count_unread(user_b.id, clinic_b.id)
    assert count_b == 1
