"""Tests unitarios: agregador de citas por periodo (BE-015-T02).

Depende de: BE-015-T01 (schemas ``report_schemas.py``).

Objetivo: verificar que ``report_appointments``:

- filtra por ``clinic_id`` (tenant isolation)
- acepta rango de fechas opcional (``period_start`` / ``period_end``)
- retorna paginación coherente (``page`` / ``size`` / ``total``)
- no hace ningún efecto de escritura en la sesión (solo lectura)
- devuelve ``AppointmentSummaryDto`` por cada registro

Validación:
    python -m pytest backend/app/tests/usecases/test_reports_appointments_aggregation.py -q
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.api.v1.schemas.report_schemas import (
    AppointmentSummaryDto,
    PaginatedResponse,
)
from app.application.usecases.reports.report_appointments import (
    report_appointments,
)

# ---------------------------------------------------------------------------
# Helpers de mock
# ---------------------------------------------------------------------------


def _make_session(items: list[Any] | None = None, total: int = 0) -> MagicMock:
    """Construye un ``MagicMock`` de ``Session`` SQLAlchemy idempotente.

    Cualquier cadena sobre el mock (``.filter()`` / ``.order_by()`` /
    ``.offset()`` / ``.limit()``) retorna el mismo mock, de modo que las
    cadenas múltiples de ``report_appointments`` se resuelvan siempre en
    ``count()`` y ``all()`` configuradas aquí.

    ``db.query(Model)``            -> ``session.query.return_value``
    ``.filter(...).filter(...)``   -> ``query`` (idempotente)
    ``query.count()``              -> ``total``
    ``query.order_by(...).offset(...).limit(...).all()`` -> ``items``
    """
    session: Any = MagicMock()
    query: Any = MagicMock()

    # Cadenas idempotentes
    query.filter.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    # Valores reales de lectura
    query.count.return_value = total
    query.all.return_value = items or []

    # db.query(Model).filter(...) -> query
    session.query.return_value.filter.return_value = query
    return session


def _make_appointment(
    id: int,
    clinic_id: int,
    pet_name: str | None = None,
    owner_name: str | None = None,
    veterinarian_name: str | None = None,
    appt_type: str = "consultation",
    status: str = "pending",
    start: datetime | None = None,
    end: datetime | None = None,
) -> Any:
    """Crea un objeto simulado con las propiedades que ``report_appointments``
    espera de ``Appointment`` ORM (a nivel de lectura, sin persistencia real).

    Nota: ``a.owner`` / ``a.pet`` / ``a.veterinarian`` son ``MagicMock`` por
    defecto; ``report_appointments`` verifica ``if a.owner`` / ``if a.pet`` /
    ``if a.veterinarian`` antes de acceder a los atributos.
    """
    a: Any = MagicMock()
    a.id = id
    a.clinic_id = clinic_id
    a.pet.name = pet_name
    a.owner.first_name = owner_name
    a.owner.last_name = ""
    a.veterinarian.nombre_completo = veterinarian_name
    a.appointment_type.value = appt_type
    a.status.value = status
    a.scheduled_start = start or datetime(2025, 6, 15, tzinfo=UTC)
    a.scheduled_end = end or (a.scheduled_start + timedelta(hours=1))
    return a


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def period_start() -> datetime:
    return datetime(2025, 1, 1, tzinfo=UTC)


@pytest.fixture()
def period_end() -> datetime:
    return datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Tests: estructura paginada y DTO por item
# ---------------------------------------------------------------------------


class TestReportAppointmentsStructure:
    def test_returns_paginated_structure_empty(self):
        session = _make_session(items=[], total=0)
        resp = report_appointments(db=session, clinic_id=1)
        assert isinstance(resp, PaginatedResponse)
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.size == 20

    def test_returns_dto_items_with_all_fields(self):
        item = _make_appointment(
            id=1,
            clinic_id=1,
            pet_name="Max",
            owner_name="Juan",
            veterinarian_name="Dr. Lopez",
            appt_type="consultation",
            status="confirmed",
            start=datetime(2025, 6, 10, 9, tzinfo=UTC),
            end=datetime(2025, 6, 10, 10, tzinfo=UTC),
        )
        session = _make_session(items=[item], total=1)
        resp = report_appointments(db=session, clinic_id=1)
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 1
        assert len(resp.items) == 1
        dto = resp.items[0]
        assert isinstance(dto, AppointmentSummaryDto)
        assert dto.id == 1
        assert dto.clinic_id == 1
        assert dto.pet_name == "Max"
        assert dto.owner_name == "Juan"
        assert dto.veterinarian_name == "Dr. Lopez"
        assert dto.appointment_type == "consultation"
        assert dto.status == "confirmed"
        assert dto.scheduled_start == datetime(2025, 6, 10, 9, tzinfo=UTC).isoformat()
        assert dto.scheduled_end == datetime(2025, 6, 10, 10, tzinfo=UTC).isoformat()

    def test_custom_page_params_propagate(self):
        session = _make_session(items=[], total=0)
        resp = report_appointments(db=session, clinic_id=1, page=3, size=5)
        assert resp.page == 3
        assert resp.size == 5


class TestReportAppointmentsNullRelationships:
    """Cuando las relaciones opcionales (pet / owner / veterinarian) son None,
    el DTO debe reflejar ``None`` para esos campos."""

    def test_none_relationships_yield_none_in_dto(self):
        a: Any = MagicMock()
        a.id = 42
        a.clinic_id = 1
        # Forzar relaciones a None (Mock por defecto es truthy; usar spec)
        a.pet = None
        a.owner = None
        a.veterinarian = None
        a.appointment_type.value = "surgery"
        a.status.value = "completed"
        a.scheduled_start = datetime(2025, 3, 1, 8, tzinfo=UTC)
        a.scheduled_end = datetime(2025, 3, 1, 9, tzinfo=UTC)

        session = _make_session(items=[a], total=1)
        resp = report_appointments(db=session, clinic_id=1)
        dto = resp.items[0]
        assert dto.pet_name is None
        assert dto.owner_name is None
        assert dto.veterinarian_name is None
        assert dto.id == 42


# ---------------------------------------------------------------------------
# Tests: aislamiento por clínica (tenant isolation)
# ---------------------------------------------------------------------------


class TestReportAppointmentsClinicIsolation:
    def test_data_separated_by_clinic(self):
        # clnica 1: 1 cita
        session_1 = _make_session(
            items=[_make_appointment(id=100, clinic_id=1)], total=1
        )
        # clnica 2: 0 citas
        session_2 = _make_session(items=[], total=0)

        resp_1 = report_appointments(db=session_1, clinic_id=1)
        resp_2 = report_appointments(db=session_2, clinic_id=2)

        assert resp_1.total == 1
        assert resp_1.items[0].clinic_id == 1
        assert resp_2.total == 0
        # El filtro por clinica se aplica en ambas sesiones
        session_1.query.return_value.filter.assert_called()
        session_2.query.return_value.filter.assert_called()


# ---------------------------------------------------------------------------
# Tests: filtro por rango de fechas
# ---------------------------------------------------------------------------


class TestReportAppointmentsPeriodFilter:
    def test_with_full_period(self, period_start, period_end):
        items = [
            _make_appointment(
                id=i + 1, clinic_id=1, start=datetime(2025, 1, i + 5, tzinfo=UTC)
            )
            for i in range(5)
        ]
        session = _make_session(items=items, total=5)
        resp = report_appointments(
            db=session,
            clinic_id=1,
            period_start=period_start,
            period_end=period_end,
        )
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 5
        assert len(resp.items) == 5

    def test_period_start_only(self, period_start):
        session = _make_session(items=[], total=0)
        resp = report_appointments(db=session, clinic_id=1, period_start=period_start)
        assert isinstance(resp, PaginatedResponse)

    def test_period_end_only(self, period_end):
        session = _make_session(items=[], total=0)
        resp = report_appointments(db=session, clinic_id=1, period_end=period_end)
        assert isinstance(resp, PaginatedResponse)

    def test_period_does_not_break_pagination_invariant(self, period_start, period_end):
        """Con items paginados, el total y len() siguen coincidiendo."""
        all_items = [
            _make_appointment(
                id=i + 1, clinic_id=1, start=datetime(2025, 1, i + 5, tzinfo=UTC)
            )
            for i in range(7)
        ]
        session = _make_session(items=all_items, total=7)
        resp = report_appointments(
            db=session,
            clinic_id=1,
            period_start=period_start,
            period_end=period_end,
        )
        assert resp.total == 7
        assert len(resp.items) == 7
        assert resp.page == 1
        assert resp.size == 20


# ---------------------------------------------------------------------------
# Tests: sin persistencia (solo lectura)
# ---------------------------------------------------------------------------


class TestReportAppointmentsNoPersistence:
    def test_no_write_side_effects(self):
        session = _make_session(items=[], total=0)
        report_appointments(db=session, clinic_id=1)
        # La función solo hace lectura: ningún método de escritura se invoca
        session.add.assert_not_called()
        session.flush.assert_not_called()
        session.delete.assert_not_called()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()

    def test_no_new_records_even_with_data(self):
        items = [_make_appointment(id=i + 1, clinic_id=1) for i in range(3)]
        session = _make_session(items=items, total=3)
        before_len = len(items)
        resp = report_appointments(db=session, clinic_id=1)
        assert len(items) == before_len  # no se agregó nada
        assert resp.total == 3
        session.add.assert_not_called()
        session.commit.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: múltiples filtros combinados no rompen la lectura
# ---------------------------------------------------------------------------


class TestReportAppointmentsCombined:
    def test_no_period_no_error(self):
        session = _make_session(items=[], total=0)
        resp = report_appointments(db=session, clinic_id=999)
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 0

    def test_all_fields_consistent_with_input(self):
        items = [
            _make_appointment(
                id=1,
                clinic_id=7,
                pet_name="Kitty",
                owner_name="Mar",
                veterinarian_name="Dr. Ana",
                appt_type="vaccination",
                status="approved",
                start=datetime(2025, 4, 1, 10, tzinfo=UTC),
                end=datetime(2025, 4, 1, 11, tzinfo=UTC),
            )
        ]
        session = _make_session(items=items, total=1)
        resp = report_appointments(db=session, clinic_id=7)
        dto = resp.items[0]
        assert dto.clinic_id == 7
        assert dto.pet_name == "Kitty"
        assert dto.owner_name == "Mar"
        assert dto.veterinarian_name == "Dr. Ana"
        assert dto.appointment_type == "vaccination"
        assert dto.status == "approved"


# ---------------------------------------------------------------------------
# Tests: ordenamiento determinista (BE-015 QA regression)
# ---------------------------------------------------------------------------


class TestReportAppointmentsDeterministicOrdering:
    """Bloquea el defecto de paginación no determinista observado en QA-015.

    Con ``ORDER BY scheduled_start DESC`` sin tiebreaker, dos filas con la
    misma ``scheduled_start`` pueden intercambiarse de posición entre una y
    otra petición, lo que produce *overlap* / *missing rows* entre páginas.

    La solución: ``order_by(scheduled_start.desc(), id.desc())``.

    La prueba no puede detectar el bug con ``MagicMock`` si sólo hace
    ``assert_called`` (acepta 1 ó N columnas); exige la lista exacta de
    columnas, en el orden exacto, para que una regresión de una sola columna
    haga fallar este test.
    """

    def test_order_by_uses_scheduled_start_then_id(self):
        from app.infrastructure.database.models.appointment import Appointment

        session = _make_session(items=[], total=0)
        report_appointments(db=session, clinic_id=1)
        # La cadena ``session.query(Model)`` returns mock A;
        # ``A.filter(...)`` returns mock B (el ``query`` interno del helper);
        # ``order_by`` es llamado sobre B (mock idempotente).
        args = session.query.return_value.filter.return_value.order_by.call_args_list[
            -1
        ].args
        assert len(args) == 2, (
            "report_appointments debe ordenar por scheduled_start + id "
            "para una paginación estable (QA-015 overlap en appointments)"
        )
        assert str(args[0]) == str(Appointment.scheduled_start.desc())
        assert str(args[1]) == str(Appointment.id.desc())
