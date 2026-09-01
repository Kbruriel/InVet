"""Pruebas unitarias del repositorio de notificaciones (BE-013-T03).

Cobertura por metodo del ABC NotificationRepository:
- create_if_unique: happy path + dedup (unique constraint)
- list_by_user: paginacion, filtro unread_only, aislamiento tenant
- get_by_id_for_user: ownership (IDOR/BOLA)
- mark_read: happy + ajeno (None) + inexiste (None)
- mark_all_read: count + aislamiento tenant
- get_notification_for_user_key: clave de dedup
- count_unread: conteo + aislamiento tenant
"""

from __future__ import annotations

import pytest

from app.data.notification_repo import get_notification_repo
from app.infrastructure.database.models.notification import Notification as NotificationModel

USER_A = 1
USER_B = 2
CLINIC_1 = 100


async def _create(
    repo,
    user_id: int = USER_A,
    clinic_id: int = CLINIC_1,
    event_type: str = "appointment_created",
    ref_type: str = "appointment",
    ref_id: int | None = 1,
    is_read: bool = False,
):
    """Crea una notificacion y devuelve el dominio."""
    n = await repo.create_if_unique(
        clinic_id=clinic_id,
        user_id=user_id,
        event_type=event_type,
        subject=f" Sujeto {event_type} ",
        body=f"cuerpo para {ref_type} {ref_id}",
        ref_type=ref_type,
        ref_id=ref_id,
    )
    if is_read and n is not None:
        await repo.mark_read(n.id, user_id)
    return n


@pytest.mark.asyncio
async def test_create_if_unique_happy_path(db_session):
    repo = get_notification_repo(db_session)
    n = await _create(repo, event_type="appointment_created", ref_id=7)
    assert n is not None
    assert n.id is not None
    assert n.clinic_id == CLINIC_1
    assert n.user_id == USER_A
    assert n.event_type == "appointment_created"
    assert n.is_read is False
    assert n.read_at is None


@pytest.mark.asyncio
async def test_create_if_unique_dedup_same_key_returns_none(db_session):
    repo = get_notification_repo(db_session)
    n1 = await _create(repo, ref_id=99)
    assert n1 is not None
    # Doble emision con la misma clave (user_id, event_type, ref_type, ref_id)
    dup = await repo.create_if_unique(
        clinic_id=CLINIC_1,
        user_id=USER_A,
        event_type="appointment_created",
        subject="Duplicada",
        body="doble",
        ref_type="appointment",
        ref_id=99,
    )
    assert dup is None
    count = await repo.count_unread(USER_A, CLINIC_1)
    assert count == 1, "la doble emision no debe insertar una segunda fila"


@pytest.mark.asyncio
async def test_create_if_unique_same_event_different_ref_ok(db_session):
    repo = get_notification_repo(db_session)
    n1 = await _create(repo, ref_id=1)
    n2 = await _create(repo, ref_id=2)
    assert n1 is not None and n2 is not None
    assert n1.id != n2.id


@pytest.mark.asyncio
async def test_list_by_user_pagination_and_unread_filter(db_session):
    repo = get_notification_repo(db_session)
    for i in range(1, 6):
        await _create(repo, ref_id=i)
    # leer las 3 primeras -> quedan 2 no leidas
    items, total = await repo.list_by_user(USER_A, CLINIC_1, page=1, page_size=10)
    assert total == 5
    marked = 0
    for it in items:
        if marked < 3:
            await repo.mark_read(it.id, USER_A)
            marked += 1
    assert marked == 3

    items_unread, total_unread = await repo.list_by_user(
        USER_A, CLINIC_1, unread_only=True
    )
    assert total_unread == 2
    assert len(items_unread) == 2
    assert all(it.is_read is False for it in items_unread)

    # paginacion: page_size=2, page=2 -> 2 items
    items_p2, total_p = await repo.list_by_user(USER_A, CLINIC_1, page=2, page_size=2)
    assert total_p == 5
    assert len(items_p2) == 2

    # pagina fuera de rango -> vacio
    items_empty, _ = await repo.list_by_user(USER_A, CLINIC_1, page=99, page_size=2)
    assert items_empty == []


@pytest.mark.asyncio
async def test_list_by_user_tenant_isolation(db_session):
    repo = get_notification_repo(db_session)
    await _create(repo, clinic_id=CLINIC_1, user_id=USER_A)
    # mismo user_id sin la clinica correcta -> 0
    items, total = await repo.list_by_user(USER_A, 999999)
    assert total == 0 and items == []
    # otro tenant con user B no ve nada
    await _create(repo, clinic_id=CLINIC_1, user_id=USER_B)
    items_b, total_b = await repo.list_by_user(USER_B, 999999)
    assert total_b == 0 and items_b == []


@pytest.mark.asyncio
async def test_get_by_id_for_user_ownership(db_session):
    repo = get_notification_repo(db_session)
    n = await _create(repo, user_id=USER_A)
    assert n is not None

    # receptor correcto la ve
    fetched = await repo.get_by_id_for_user(n.id, USER_A)
    assert fetched is not None and fetched.id == n.id

    # usuario ajeno NO puede leerla (BOLA/IDOR) -> None
    assert await repo.get_by_id_for_user(n.id, USER_B) is None

    # ID inexistente -> None
    assert await repo.get_by_id_for_user(987654, USER_A) is None


@pytest.mark.asyncio
async def test_mark_read_updates_flags(db_session):
    repo = get_notification_repo(db_session)
    n = await _create(repo, ref_id=42)
    assert n is not None
    marked = await repo.mark_read(n.id, USER_A)
    assert marked is not None
    assert marked.is_read is True
    assert marked.read_at is not None
    assert await repo.count_unread(USER_A, CLINIC_1) == 0


@pytest.mark.asyncio
async def test_mark_read_foreign_returns_none(db_session):
    repo = get_notification_repo(db_session)
    n = await _create(repo, user_id=USER_A)
    assert n is not None
    # usuario ajeno no puede marcarla -> None (sin revelar existencia)
    assert await repo.mark_read(n.id, USER_B) is None
    # la notificacion sigue no leida para el receptor
    assert (await repo.get_by_id_for_user(n.id, USER_A)).is_read is False


@pytest.mark.asyncio
async def test_mark_all_read_count_and_tenant_scope(db_session):
    repo = get_notification_repo(db_session)
    for i in range(1, 4):
        await _create(repo, user_id=USER_A, ref_id=i)
    await _create(repo, user_id=USER_B, ref_id=1)

    count_a = await repo.mark_all_read(USER_A, CLINIC_1)
    assert count_a == 3
    # usuario B no tocado, su conteo no leido intacto
    assert await repo.count_unread(USER_B, CLINIC_1) == 1
    # re-marcar todo -> 0 nuevas
    assert await repo.mark_all_read(USER_A, CLINIC_1) == 0

    # tenant equivocado para el receptor -> 0
    assert await repo.mark_all_read(USER_A, 999999) == 0


@pytest.mark.asyncio
async def test_count_unread_tenant_isolation(db_session):
    repo = get_notification_repo(db_session)
    await _create(repo, clinic_id=CLINIC_1, user_id=USER_A)
    assert await repo.count_unread(USER_A, CLINIC_1) == 1
    assert await repo.count_unread(USER_A, 999999) == 0
    assert await repo.count_unread(USER_B, CLINIC_1) == 0


@pytest.mark.asyncio
async def test_get_notification_for_user_key_dedup_key(db_session):
    repo = get_notification_repo(db_session)
    n = await _create(repo, event_type="payment_received", ref_type="payment", ref_id=555)
    assert n is not None
    found = await repo.get_notification_for_user_key(
        user_id=USER_A, event_type="payment_received", ref_type="payment", ref_id=555
    )
    assert found is not None and found.id == n.id
    # clave distinta -> None
    assert (
        await repo.get_notification_for_user_key(
            user_id=USER_A, event_type="payment_received", ref_type="payment", ref_id=556
        )
        is None
    )
    # otro receptor con misma clave -> None
    assert (
        await repo.get_notification_for_user_key(
            user_id=USER_B, event_type="payment_received", ref_type="payment", ref_id=555
        )
        is None
    )


@pytest.mark.asyncio
async def test_orm_model_registered_in_metadata(db_session):
    """T03 requisito: la tabla notifications + constraint de dedup existen en el metadata."""
    from sqlalchemy import inspect

    inspector = inspect(db_session.bind)
    assert "notifications" in inspector.get_table_names()
    model_table = NotificationModel.__table__
    assert model_table.name == "notifications"
    unique_names = [c.name for c in model_table.constraints if c.name]
    assert "uq_notifications_dedup" in unique_names
    # la unique constraint dedup debe estar presente en la DDL creada
    unique_constraints = [
        c.get("name")
        for c in inspector.get_unique_constraints("notifications")
        if c.get("name")
    ]
    assert "uq_notifications_dedup" in unique_constraints
