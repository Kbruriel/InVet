"""Pruebas unitarias de reglas de dominio — soporte basico (BE-014-T03).

Validacion: Pruebas unitarias de reglas (AC-01, AC-05).

Reglas cubiertas:
- create_ticket:
  * titulo < 5 caracteres  -> ValueError
  * titulo >= 5 caracteres -> OK
  * titulo duplicado en las ultimas 24 h -> DuplicateSupportTicketError
- change_status (transiciones validas por estado actual):
  * iniciado   -> pendiente  OK
  * iniciado   -> proceso    OK
  * iniciado   -> completado ValueError  (saltar estados)
  * iniciado   -> cerrado    ValueError
  * pendiente  -> proceso    OK
  * pendiente  -> cerrado    ValueError
  * proceso    -> completado OK
  * proceso    -> cerrado    OK
  * proceso    -> pendiente  ValueError  (no se puede retroceder)
  * completado -> (ninguno)  ValueError  (terminal)
  * cerrado    -> (ninguno)  ValueError  (terminal)
  * estado inexistente      -> ValueError
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.application.support_ticket_use_cases import (
    DuplicateSupportTicketError,
    SupportTicketService,
)


def _domain(
    id=1,
    title="t",
    desc=None,
    status="iniciado",
    cat_id=None,
    owner_id=1,
    clinic_id=1,
    created_at=None,
    updated_at=None,
):
    """Fábrica mock de dominio."""
    from types import SimpleNamespace

    return SimpleNamespace(
        id=id,
        title=title,
        description=desc,
        status=status,
        category_id=cat_id,
        owner_id=owner_id,
        clinic_id=clinic_id,
        created_at=created_at,
        updated_at=updated_at,
    )


def _category(id=1, name="C"):
    from types import SimpleNamespace

    return SimpleNamespace(id=id, name=name)


def make_service(repo: AsyncMock) -> SupportTicketService:
    return SupportTicketService(repo=repo)


def _repo_for_transition(old_status: str, new_status: str) -> AsyncMock:
    repo = AsyncMock()
    repo.get_by_id_for_owner = AsyncMock(
        return_value=(_domain(status=old_status), None)
    )
    repo.update_status = AsyncMock(return_value=(old_status, new_status))
    return repo


# ===========================================================================
# create_ticket — validacion de titulo
# ===========================================================================


@pytest.mark.asyncio
async def test_create_title_too_short_raises():
    """AC-01: titulo < 5 chars -> ValueError."""
    repo = AsyncMock()
    svc = make_service(repo)
    with pytest.raises(ValueError, match="al menos 5"):
        await svc.create_ticket(
            title="abcd",  # 4 chars
            description=None,
            category_id=None,
            owner_id=1,
            clinic_id=1,
        )
    assert (
        not repo.create_ticket.called
    ), "Repo no debe llamarse si el titulo es invalido"


@pytest.mark.asyncio
async def test_create_title_exactly_5_ok():
    """AC-01: titulo de exactamente 5 chars -> OK (no error)."""
    repo = AsyncMock()
    domain = _domain(title="abcde")
    repo.find_recent_duplicate = AsyncMock(return_value=False)
    repo.create_ticket = AsyncMock(return_value=(domain, _category()))
    svc = make_service(repo)

    result = await svc.create_ticket(
        title="abcde",
        description=None,
        category_id=None,
        owner_id=1,
        clinic_id=1,
    )
    assert result["title"] == "abcde"
    assert result["status"] == "iniciado"
    repo.create_ticket.assert_called_once()


@pytest.mark.asyncio
async def test_create_duplicate_within_24_hours_raises():
    """AC-01: un titulo equivalente reciente no crea un segundo ticket."""
    from datetime import UTC, datetime, timedelta

    before = datetime.now(UTC) - timedelta(hours=24, seconds=1)
    repo = AsyncMock()
    repo.find_recent_duplicate = AsyncMock(return_value=True)
    svc = make_service(repo)

    with pytest.raises(DuplicateSupportTicketError, match="ultimas 24 horas"):
        await svc.create_ticket(
            title="  Problema con mi mascota  ",
            description=None,
            category_id=None,
            owner_id=7,
            clinic_id=3,
        )

    repo.create_ticket.assert_not_awaited()
    kwargs = repo.find_recent_duplicate.await_args.kwargs
    assert kwargs["title"] == "Problema con mi mascota"
    assert kwargs["owner_id"] == 7
    assert kwargs["clinic_id"] == 3
    assert before <= kwargs["created_since"] <= datetime.now(UTC) - timedelta(hours=24)


@pytest.mark.asyncio
async def test_create_title_stripped_short_raises():
    """AC-01: '  ab  ' (2 chars visible, 5 con espacios) -> se strip, debe fallar."""
    # Nota: la logica usa title.strip() — 'ab   ' -> 'ab' -> len 2 -> raises
    repo = AsyncMock()
    svc = make_service(repo)
    with pytest.raises(ValueError, match="al menos 5"):
        await svc.create_ticket(
            title="ab   ",  # strip -> "ab" — 2 chars
            description=None,
            category_id=None,
            owner_id=1,
            clinic_id=1,
        )


# ===========================================================================
# change_status — transiciones validas e invalidas (AC-05)
# ===========================================================================


@pytest.mark.asyncio
async def test_transition_iniciado_pendiente_ok():
    """AC-05: iniciado -> pendiente es valida."""
    repo = _repo_for_transition("iniciado", "pendiente")
    svc = make_service(repo)

    result = await svc.change_status(
        ticket_id=1,
        owner_id=1,
        clinic_id=1,
        new_status="pendiente",
    )
    assert result["old_status"] == "iniciado"
    assert result["new_status"] == "pendiente"


@pytest.mark.asyncio
async def test_transition_iniciado_proceso_ok():
    """AC-05: iniciado -> proceso es valida."""
    repo = _repo_for_transition("iniciado", "proceso")
    svc = make_service(repo)

    result = await svc.change_status(
        ticket_id=1,
        owner_id=1,
        clinic_id=1,
        new_status="proceso",
    )
    assert result["new_status"] == "proceso"


@pytest.mark.asyncio
async def test_transition_iniciado_completado_raises():
    """AC-05: iniciado -> completado es INVALIDA (salta estados)."""
    repo = _repo_for_transition("iniciado", "completado")
    svc = make_service(repo)

    with pytest.raises(ValueError, match="Transicion invalida"):
        await svc.change_status(
            ticket_id=1,
            owner_id=1,
            clinic_id=1,
            new_status="completado",
        )
    repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_iniciado_cerrado_raises():
    """AC-05: iniciado -> cerrado es INVALIDA."""
    repo = _repo_for_transition("iniciado", "cerrado")
    svc = make_service(repo)

    with pytest.raises(ValueError, match="Transicion invalida"):
        await svc.change_status(
            ticket_id=1,
            owner_id=1,
            clinic_id=1,
            new_status="cerrado",
        )
    repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_pendiente_proceso_ok():
    """AC-05: pendiente -> proceso es valida."""
    repo = _repo_for_transition("pendiente", "proceso")
    svc = make_service(repo)

    result = await svc.change_status(
        ticket_id=1,
        owner_id=1,
        clinic_id=1,
        new_status="proceso",
    )
    assert result["new_status"] == "proceso"


@pytest.mark.asyncio
async def test_transition_pendiente_cerrado_raises():
    """AC-05: pendiente -> cerrado es INVALIDA (debe pasar por proceso)."""
    repo = _repo_for_transition("pendiente", "cerrado")
    svc = make_service(repo)

    with pytest.raises(ValueError, match="Transicion invalida"):
        await svc.change_status(
            ticket_id=1,
            owner_id=1,
            clinic_id=1,
            new_status="cerrado",
        )
    repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_proceso_completado_ok():
    """AC-05: proceso -> completado es valida."""
    repo = _repo_for_transition("proceso", "completado")
    svc = make_service(repo)

    result = await svc.change_status(
        ticket_id=1,
        owner_id=1,
        clinic_id=1,
        new_status="completado",
    )
    assert result["new_status"] == "completado"


@pytest.mark.asyncio
async def test_transition_proceso_cerrado_ok():
    """AC-05: proceso -> cerrado es valida."""
    repo = _repo_for_transition("proceso", "cerrado")
    svc = make_service(repo)

    result = await svc.change_status(
        ticket_id=1,
        owner_id=1,
        clinic_id=1,
        new_status="cerrado",
    )
    assert result["new_status"] == "cerrado"


@pytest.mark.asyncio
async def test_transition_proceso_pendiente_raises():
    """AC-05: proceso -> pendiente es INVALIDA (no se permite retroceder)."""
    repo = _repo_for_transition("proceso", "pendiente")
    svc = make_service(repo)

    with pytest.raises(ValueError, match="Transicion invalida"):
        await svc.change_status(
            ticket_id=1,
            owner_id=1,
            clinic_id=1,
            new_status="pendiente",
        )
    repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_completado_any_raises():
    """AC-05: completado es TERMINAL — cualquier transicion -> ValueError."""
    for new_status in ["pendiente", "proceso", "completado", "cerrado", "iniciado"]:
        repo = _repo_for_transition("completado", new_status)
        svc = make_service(repo)
        with pytest.raises(ValueError, match="Transicion invalida"):
            await svc.change_status(
                ticket_id=1,
                owner_id=1,
                clinic_id=1,
                new_status=new_status,
            )
        repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_transition_cerrado_any_raises():
    """AC-05: cerrado es TERMINAL — cualquier transicion -> ValueError."""
    for new_status in ["pendiente", "proceso", "completado", "cerrado", "iniciado"]:
        repo = _repo_for_transition("cerrado", new_status)
        svc = make_service(repo)
        with pytest.raises(ValueError, match="Transicion invalida"):
            await svc.change_status(
                ticket_id=1,
                owner_id=1,
                clinic_id=1,
                new_status=new_status,
            )
        repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_status_unknown_old_status_raises():
    """AC-05: estado desconocido en el repo -> siempre ValueError (no hay transiciones)."""
    repo = _repo_for_transition("estado_desconocido", "pendiente")
    svc = make_service(repo)

    with pytest.raises(ValueError, match="Transicion invalida"):
        await svc.change_status(
            ticket_id=1,
            owner_id=1,
            clinic_id=1,
            new_status="pendiente",
        )
    repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_status_missing_ticket_returns_none_without_update():
    repo = AsyncMock()
    repo.get_by_id_for_owner = AsyncMock(return_value=None)
    svc = make_service(repo)

    result = await svc.change_status(
        ticket_id=999,
        owner_id=1,
        clinic_id=1,
        new_status="pendiente",
    )

    assert result is None
    repo.update_status.assert_not_awaited()


# ===========================================================================
# create_ticket — estructura de respuesta
# ===========================================================================


@pytest.mark.asyncio
async def test_create_returns_expected_shape():
    """AC-01: la respuesta incluye todos los campos obligatorios."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    repo = AsyncMock()
    domain = _domain(
        title="Soporte tecnico",
        desc="desc",
        status="iniciado",
        cat_id=1,
        owner_id=42,
        clinic_id=7,
        created_at=now,
        updated_at=now,
    )
    cat = _category(id=1, name="Generales")
    repo.find_recent_duplicate = AsyncMock(return_value=False)
    repo.create_ticket = AsyncMock(return_value=(domain, cat))
    svc = make_service(repo)

    result = await svc.create_ticket(
        title="Soporte tecnico",
        description="desc",
        category_id=1,
        owner_id=42,
        clinic_id=7,
    )
    for field in (
        "id",
        "title",
        "description",
        "status",
        "category_id",
        "category",
        "owner_id",
        "clinic_id",
        "created_at",
        "updated_at",
    ):
        assert field in result, f"Falta campo '{field}' en la respuesta"
    assert result["status"] == "iniciado"
    assert result["category"]["name"] == "Generales"
    assert result["owner_id"] == 42
    assert result["clinic_id"] == 7


@pytest.mark.asyncio
async def test_create_category_none_when_no_category():
    """AC-01: category es None cuando no se especifica."""
    repo = AsyncMock()
    domain = _domain(title="Ticket sin categoria", cat_id=None)
    repo.find_recent_duplicate = AsyncMock(return_value=False)
    repo.create_ticket = AsyncMock(return_value=(domain, None))
    svc = make_service(repo)

    result = await svc.create_ticket(
        title="Ticket sin categoria",
        description=None,
        category_id=None,
        owner_id=1,
        clinic_id=1,
    )
    assert result["category"] is None
    assert result["category_id"] is None
