"""Pruebas unitarias de seguridad del repositorio de soporte basico (BE-014-T02).

Validacion: Pruebas de lectura propia, ajena e interna (AC-03, AC-04, AC-11).

Scenarios cubiertos por metodo del port SupportTicketRepository:
- get_by_id_for_owner:
    propia  — owner lee su ticket en su clinica       -> visible
    ajena   — owner de otra clinica lee el ticket     -> None (BOLA)
    interna — otro owner de la misma clinica lee      -> None (BOLA)
    inexist — ID inexistente                          -> None
- list_by_owner:
    propia  — owner lista sus tickets                 -> visible
    ajena   — owner de otra clinica lista             -> total == 0
    interna — otro owner, misma clinica, lista        -> total == 0
- update_status:
    propia  — owner cambia estado del suyo            -> (old, new)
    ajena   — owner de otra clinica                   -> None
    interna — otro owner, misma clinica               -> None
    inexist — ID inexistente                          -> None
- list_active_categories:
    propia  — categorias de la clinica propia         -> visibles
    ajena   — categorias de otra clinica              -> [] (BOLA)
- list_by_clinic:
    interna — staff interno lista tickets de la clinica -> visibles a todos

Regla de seguridad (AC-11): un recurso ajeno no es visible para un actor
no autorizado; la respuesta no revela la existencia del recurso (None / 404).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.data.support_ticket_repo import get_support_ticket_repo
from app.infrastructure.database.models.clinic import Clinic as ClinicModel
from app.infrastructure.database.models.owner import Owner as OwnerModel
from app.infrastructure.database.models.support_ticket_model import (
    SupportTicket as SupportTicketModel,
)
from app.infrastructure.database.models.support_ticket_model import (
    TicketCategory as TicketCategoryModel,
)
from app.infrastructure.database.models.user import User as UserModel

# --------------------------------------------------------------------------- #
# Identidades test
# --------------------------------------------------------------------------- #
CLINIC_A = 1  # clinic "Alfa" — owner A es su dueño
CLINIC_B = 2  # clinic "Bet"  — owner B es su dueño
OWNER_A = 100  # owner user de clinic A
OWNER_B = 200  # owner user de clinic B (ajeno, otra clinica)
OWNER_C = 300  # owner user de clinic A (mismo tenant, otro owner -> "interna")

# --------------------------------------------------------------------------- #
# Fixture de datos (SQLite, sin FK checks reales por SQLite; se valida a nivel logico)
# --------------------------------------------------------------------------- #


@pytest.fixture
def seeded(db_session):
    """Seed: 2 clínicas, 3 owners y 1 categoria y 1 ticket por owner.

    Retorna un dict con los IDs creados.
    """
    from datetime import UTC, datetime

    now = datetime.now(UTC)

    # Clinics
    c_a = ClinicModel(
        name="Clinica Alfa",
        address="A",
        city="C",
        state="S",
        country="MX",
        postal_code="00001",
        phone="T",
    )
    c_b = ClinicModel(
        name="Clinica Bet",
        address="B",
        city="C",
        state="S",
        country="MX",
        postal_code="00002",
        phone="T",
    )
    db_session.add_all([c_a, c_b])
    db_session.flush()
    clinic_a_id, clinic_b_id = c_a.id, c_b.id

    # Users
    u_a = UserModel(
        email="a@example.com",
        username="ua",
        hashed_password="h",
        first_name="A",
        last_name="X",
    )
    u_b = UserModel(
        email="b@example.com",
        username="ub",
        hashed_password="h",
        first_name="B",
        last_name="Y",
    )
    u_c = UserModel(
        email="c@example.com",
        username="uc",
        hashed_password="h",
        first_name="C",
        last_name="Z",
    )
    db_session.add_all([u_a, u_b, u_c])
    db_session.flush()

    # Owners
    o_a = OwnerModel(
        user_id=u_a.id,
        first_name="A",
        last_name="A",
        email="oa@ex.com",
        phone="p",
        city="c",
        is_active=True,
        clinic_id=clinic_a_id,
    )
    o_b = OwnerModel(
        user_id=u_b.id,
        first_name="B",
        last_name="B",
        email="ob@ex.com",
        phone="p",
        city="c",
        is_active=True,
        clinic_id=clinic_b_id,
    )
    o_c = OwnerModel(
        user_id=u_c.id,
        first_name="C",
        last_name="C",
        email="oc@ex.com",
        phone="p",
        city="c",
        is_active=True,
        clinic_id=clinic_a_id,
    )
    db_session.add_all([o_a, o_b, o_c])
    db_session.flush()

    # Categorías — una por clínica, ambas activas
    cat_a = TicketCategoryModel(
        clinic_id=clinic_a_id,
        name="Generales",
        active=True,
        created_at=now,
    )
    cat_b = TicketCategoryModel(
        clinic_id=clinic_b_id,
        name="Urgencias",
        active=True,
        created_at=now,
    )
    db_session.add_all([cat_a, cat_b])
    db_session.flush()

    # Tickets
    t_a = SupportTicketModel(
        title="Problema con mi mascota",
        description="No come bien",
        status="iniciado",
        category_id=cat_a.id,
        owner_id=o_a.id,
        clinic_id=clinic_a_id,
        created_at=now,
        updated_at=now,
    )
    t_b = SupportTicketModel(
        title="Ticket de la clinica B",
        description="Test B",
        status="pendiente",
        category_id=cat_b.id,
        owner_id=o_b.id,
        clinic_id=clinic_b_id,
        created_at=now,
        updated_at=now,
    )
    db_session.add_all([t_a, t_b])
    db_session.commit()
    db_session.refresh(t_a)
    db_session.refresh(t_b)

    return {
        "clinic_a_id": clinic_a_id,
        "clinic_b_id": clinic_b_id,
        "owner_a_id": o_a.id,
        "owner_b_id": o_b.id,
        "owner_c_id": o_c.id,
        "cat_a_id": cat_a.id,
        "cat_b_id": cat_b.id,
        "ticket_a_id": t_a.id,
        "ticket_b_id": t_b.id,
    }


# ============================================================================= #
# find_recent_duplicate — ventana de 24 h y aislamiento
# ============================================================================= #


@pytest.mark.asyncio
async def test_find_recent_duplicate_matches_normalized_title(db_session, seeded):
    repo = get_support_ticket_repo(db_session)

    found = await repo.find_recent_duplicate(
        title="  PROBLEMA CON MI MASCOTA ",
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
        created_since=datetime.now(UTC) - timedelta(hours=24),
    )

    assert found is True


@pytest.mark.asyncio
async def test_find_recent_duplicate_respects_window_and_identity(db_session, seeded):
    repo = get_support_ticket_repo(db_session)
    since = datetime.now(UTC) - timedelta(hours=24)

    assert (
        await repo.find_recent_duplicate(
            "Problema con mi mascota",
            seeded["owner_b_id"],
            seeded["clinic_a_id"],
            since,
        )
        is False
    )
    assert (
        await repo.find_recent_duplicate(
            "Otro titulo",
            seeded["owner_a_id"],
            seeded["clinic_a_id"],
            since,
        )
        is False
    )
    assert (
        await repo.find_recent_duplicate(
            "Problema con mi mascota",
            seeded["owner_a_id"],
            seeded["clinic_a_id"],
            datetime.now(UTC) + timedelta(seconds=1),
        )
        is False
    )


# ============================================================================= #
# get_by_id_for_owner — lectura propia / ajena / interna
# ============================================================================= #


@pytest.mark.asyncio
async def test_get_by_id_own_returns_ticket(db_session, seeded):
    """AC-04 propia: owner A ve su ticket en clinica A."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.get_by_id_for_owner(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
    )
    assert result is not None, "Owner A no pudo ver su propio ticket"
    domain, _cat = result
    assert domain.id == seeded["ticket_a_id"]
    assert domain.owner_id == seeded["owner_a_id"]


@pytest.mark.asyncio
async def test_get_by_id_foreign_clinic_returns_none(db_session, seeded):
    """AC-04/AC-11 ajena: owner B (clinica B) no ve ticket de clinica A."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.get_by_id_for_owner(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_b_id"],
        clinic_id=seeded["clinic_b_id"],
    )
    assert result is None, "Owner B (ajeno) pudo leer el ticket de clinica A — BOLA"


@pytest.mark.asyncio
async def test_get_by_id_same_clinic_other_owner_returns_none(db_session, seeded):
    """AC-04/AC-11 interna: owner C (misma clinica A, pero otro owner) no ve ticket de A."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.get_by_id_for_owner(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_c_id"],
        clinic_id=seeded["clinic_a_id"],
    )
    assert (
        result is None
    ), "Owner C (mismo tenant, otro owner) pudo leer ticket de A — BOLA"


@pytest.mark.asyncio
async def test_get_by_id_nonexistent_returns_none(db_session, seeded):
    """AC-04: ID inexistente -> None (sin revelar existencia)."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.get_by_id_for_owner(
        ticket_id=999999,
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
    )
    assert result is None


# ============================================================================= #
# list_by_owner — listado propia / ajena / interna
# ============================================================================= #


@pytest.mark.asyncio
async def test_list_by_owner_own_returns_visible(db_session, seeded):
    """AC-03 propia: owner A puede listar su ticket en clinica A."""
    repo = get_support_ticket_repo(db_session)
    items, total = await repo.list_by_owner(
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
        page=1,
        page_size=20,
    )
    assert total >= 1, "Owner A no ve su ticket en el listado"
    ticket_ids = [d.id for d, _ in items]
    assert seeded["ticket_a_id"] in ticket_ids


@pytest.mark.asyncio
async def test_list_by_owner_foreign_clinic_empty(db_session, seeded):
    """AC-03/AC-11 ajena: owner B (clinica B) no ve tickets de clinica A."""
    repo = get_support_ticket_repo(db_session)
    _, total = await repo.list_by_owner(
        owner_id=seeded["owner_b_id"],
        clinic_id=seeded[
            "clinic_a_id"
        ],  # intencionalmente "ajeno" a B (B no tiene en A)
        page=1,
        page_size=20,
    )
    # owner B no es owner de clinic A; el repo filtra por owner_id AND clinic_id.
    # Como owner_id B != owner_id A, total == 0.
    assert total == 0, "Owner B pudo listar tickets de clinic A con su owner_id — BOLA"


@pytest.mark.asyncio
async def test_list_by_owner_same_clinic_other_owner_empty(db_session, seeded):
    """AC-11 interna: owner C (mismia clinica A) no ve tickets de owner A."""
    repo = get_support_ticket_repo(db_session)
    _, total = await repo.list_by_owner(
        owner_id=seeded["owner_c_id"],
        clinic_id=seeded["clinic_a_id"],
        page=1,
        page_size=20,
    )
    assert total == 0, "Owner C (mismo tenant) pudo listar tickets de owner A — BOLA"


@pytest.mark.asyncio
async def test_list_by_owner_with_status_filter(db_session, seeded):
    """AC-03: filtro por estado en el listado.
    Crea un ticket adicional en estado 'pendiente' para owner A y verifica
    que el filtro 'pendiente' lo incluye, pero el filtro 'iniciado' no."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    extra = SupportTicketModel(
        title="Otro ticket pendiente",
        description="desc",
        status="pendiente",
        category_id=None,
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
        created_at=now,
        updated_at=now,
    )
    db_session.add(extra)
    db_session.commit()

    repo = get_support_ticket_repo(db_session)
    # Filtro "pendiente" debe incluir al menos el extra
    items_pend, total_pend = await repo.list_by_owner(
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
        page=1,
        page_size=20,
        status="pendiente",
    )
    assert extra.id in [
        d.id for d, _ in items_pend
    ], "Filtro pendiente no incluye el ticket pendiente"

    # El ticket "iniciado" original NO debe aparecer en el filtro "pendiente"
    assert seeded["ticket_a_id"] not in [
        d.id for d, _ in items_pend
    ], "El ticket 'iniciado' aparece en el filtro 'pendiente'"


# ============================================================================= #
# update_status — propia / ajena / interna
# ============================================================================= #


@pytest.mark.asyncio
async def test_update_status_own_succeeds(db_session, seeded):
    """AC-05 propia: owner A cambia estado de su ticket (iniciado -> pendiente)."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.update_status(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
        new_status="pendiente",
    )
    assert result is not None, "Owner A no pudo actualizar el estado de su ticket"
    old_status, new_status = result
    assert old_status == "iniciado"
    assert new_status == "pendiente"


@pytest.mark.asyncio
async def test_update_status_foreign_clinic_returns_none(db_session, seeded):
    """AC-05/AC-11 ajena: owner B no puede cambiar estado de ticket de clinic A."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.update_status(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_b_id"],
        clinic_id=seeded["clinic_b_id"],
        new_status="pendiente",
    )
    assert result is None, "Owner B pudo cambiar el estado de un ticket ajeno — IDOR"


@pytest.mark.asyncio
async def test_update_status_same_clinic_other_owner_returns_none(db_session, seeded):
    """AC-05/AC-11 interna: owner C (mismia clinica) no cambia estado de ticket de A."""
    repo = get_support_ticket_repo(db_session)
    result = await repo.update_status(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_c_id"],
        clinic_id=seeded["clinic_a_id"],
        new_status="pendiente",
    )
    assert (
        result is None
    ), "Owner C pudo cambiar el estado de un ticket de otro owner — BOLA"


@pytest.mark.asyncio
async def test_update_status_preserves_original_state_when_denied(db_session, seeded):
    """AC-11: una negacion (ajeno/interno) no modifica el estado original."""
    repo = get_support_ticket_repo(db_session)
    # Intento de owner B — debe denegarse sin cambios
    await repo.update_status(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_b_id"],
        clinic_id=seeded["clinic_b_id"],
        new_status="completado",
    )
    # Verificar estado inalterado
    result = await repo.get_by_id_for_owner(
        ticket_id=seeded["ticket_a_id"],
        owner_id=seeded["owner_a_id"],
        clinic_id=seeded["clinic_a_id"],
    )
    assert result is not None
    domain, _ = result
    assert (
        domain.status == "iniciado"
    ), f"Estado original modificado por acceso ajeno: esperado 'iniciado', got '{domain.status}'"


# ============================================================================= #
# list_active_categories — aislamiento por clinica
# ============================================================================= #


@pytest.mark.asyncio
async def test_list_categories_own_clinic(db_session, seeded):
    """AC-02: categorias de clinica A son visibles para owner A."""
    repo = get_support_ticket_repo(db_session)
    cats = await repo.list_active_categories(clinic_id=seeded["clinic_a_id"])
    names = [c.name for c in cats]
    assert (
        "Generales" in names
    ), f"Categoria de propia clinica A no encontrada en {names}"


@pytest.mark.asyncio
async def test_list_categories_ajena_clinic_excluded(db_session, seeded):
    """AC-02/AC-11: categorias de clinic B no se filtran por clinic A (aislamiento)."""
    repo = get_support_ticket_repo(db_session)
    cats_a = await repo.list_active_categories(clinic_id=seeded["clinic_a_id"])
    # Las categorias de clinic B ("Urgencias") NO deben aparecer en clinic A
    names_a = [c.name for c in cats_a]
    assert (
        "Urgencias" not in names_a
    ), "Categorias de clinic B aparecen en el listado de clinic A — BOLA de categorias"


@pytest.mark.asyncio
async def test_list_categories_only_active(db_session, seeded):
    """AC-02: categorias inactivas no se devuelven."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    # crear categoria inactiva en clinic A
    cat_inact = TicketCategoryModel(
        clinic_id=seeded["clinic_a_id"],
        name="Categoria inactiva",
        active=False,
        created_at=now,
    )
    db_session.add(cat_inact)
    db_session.commit()

    repo = get_support_ticket_repo(db_session)
    cats = await repo.list_active_categories(clinic_id=seeded["clinic_a_id"])
    names = [c.name for c in cats]
    assert (
        "Categoria inactiva" not in names
    ), "Categoria inactiva se devolvió en el listado de activas"


# ============================================================================= #
# list_by_clinic — acceso interno (AC-11 "consultas aisladas por clínica")
# ============================================================================= #


@pytest.mark.asyncio
async def test_list_by_clinic_sees_all_owners_in_clinic(db_session, seeded):
    """AC-11/AC-03: list_by_clinic devuelve tickets de TODOS los owners de la clinic.
    (Usado por el personal interno para ver tickets de su clínica, no por owner propio.)
    """
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    # owner C (mismia clinic A) tiene su propio ticket; crearlo
    t_c = SupportTicketModel(
        title="Ticket de owner C clinic A",
        description="desc",
        status="iniciado",
        category_id=None,
        owner_id=seeded["owner_c_id"],
        clinic_id=seeded["clinic_a_id"],
        created_at=now,
        updated_at=now,
    )
    db_session.add(t_c)
    db_session.commit()

    repo = get_support_ticket_repo(db_session)
    items, total = await repo.list_by_clinic(
        clinic_id=seeded["clinic_a_id"],
        page=1,
        page_size=20,
    )
    # Clinic A debe tener al menos los tickets de A y C
    ids = [d.id for d, _ in items]
    assert seeded["ticket_a_id"] in ids, "list_by_clinic no incluye ticket de owner A"
    assert t_c.id in ids, "list_by_clinic no incluye ticket de owner C"
    # Clinic B NO debe aparecer
    assert (
        seeded["ticket_b_id"] not in ids
    ), "list_by_clinic de A incluye ticket de clinic B — BOLA"
