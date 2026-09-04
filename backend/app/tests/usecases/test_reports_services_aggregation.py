"""Tests unitarios: agregador de servicios por periodo (BE-015-T03).

Depende de: BE-015-T01 (schemas ``report_schemas.py``).

Objetivo: verificar que ``report_services``:

- filtra por ``clinic_id`` (tenant isolation)
- acepta rango de fechas opcional (``period_start`` / ``period_end``)
- retorna paginación coherente (``page`` / ``size`` / ``total``)
- no hace ningún efecto de escritura en la sesión (solo lectura)
- convierte ``price`` (cents int en DB) a pesos (float) fiel al repo BE-006
- devuelve ``ServiceSummaryDto`` por cada registro

Validación:
    python -m pytest backend/app/tests/usecases/test_reports_services_aggregation.py -q
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.api.v1.schemas.report_schemas import (
    PaginatedResponse,
    ServiceSummaryDto,
)
from app.application.usecases.reports.report_services import report_services

# ---------------------------------------------------------------------------
# Helpers de mock
# ---------------------------------------------------------------------------


def _make_session(items: list[Any] | None = None, total: int = 0) -> MagicMock:
    """Construye un ``MagicMock`` de ``Session`` SQLAlchemy idempotente.

    Cualquier cadena sobre el mock (``.filter()`` / ``.order_by()`` /
    ``.offset()`` / ``.limit()``) retorna el mismo mock, de modo que las
    cadenas múltiples de ``report_services`` se resuelvan siempre en
    ``count()`` y ``all()`` configuradas aquí.
    """
    session: Any = MagicMock()
    query: Any = MagicMock()

    query.filter.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.count.return_value = total
    query.all.return_value = items or []

    session.query.return_value.filter.return_value = query
    return session


def _make_service(
    id: int,
    clinic_id: int,
    name: str = "Vacuna rabia",
    description: str | None = "Rabies vaccine",
    price_cents: int = 5000,
    duration_minutes: int = 30,
    is_active: bool = True,
    created: datetime | None = None,
) -> Any:
    """Crea un objeto simulado con las propiedades que ``report_services``
    espera de ``Service`` ORM (a nivel de lectura, sin persistencia real).
    """
    s: Any = MagicMock()
    s.id = id
    s.clinic_id = clinic_id
    s.name = name
    s.description = description
    s.price = price_cents
    s.duration_minutes = duration_minutes
    s.is_active = is_active
    s.created_at = created or datetime(2025, 6, 15, tzinfo=UTC)
    return s


# ---------------------------------------------------------------------------
# Tests: estructura paginada y DTO por item
# ---------------------------------------------------------------------------


class TestReportServicesStructure:
    def test_returns_paginated_structure_empty(self):
        session = _make_session(items=[], total=0)
        resp = report_services(db=session, clinic_id=1)
        assert isinstance(resp, PaginatedResponse)
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.size == 20

    def test_returns_dto_items_with_all_fields(self):
        item = _make_service(
            id=10,
            clinic_id=42,
            name="Desparasitación",
            description="Antiparasitario interno",
            price_cents=2500,
            duration_minutes=15,
            is_active=True,
        )
        session = _make_session(items=[item], total=1)
        resp = report_services(db=session, clinic_id=42)
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 1
        assert len(resp.items) == 1
        dto = resp.items[0]
        assert isinstance(dto, ServiceSummaryDto)
        assert dto.id == 10
        assert dto.clinic_id == 42
        assert dto.name == "Desparasitación"
        assert dto.description == "Antiparasitario interno"
        assert dto.price == 25.0
        assert dto.duration_minutes == 15
        assert dto.is_active is True

    def test_price_converted_from_cents_to_pesos(self):
        item = _make_service(id=1, clinic_id=1, price_cents=5000)
        session = _make_session(items=[item], total=1)
        resp = report_services(db=session, clinic_id=1)
        assert resp.items[0].price == 50.0

    def test_none_price_yields_zero(self):
        s: Any = MagicMock()
        s.id = 5
        s.clinic_id = 1
        s.name = "X"
        s.description = None
        s.price = None
        s.duration_minutes = 1
        s.is_active = False
        s.created_at = datetime(2025, 1, 1, tzinfo=UTC)
        session = _make_session(items=[s], total=1)
        resp = report_services(db=session, clinic_id=1)
        assert resp.items[0].price == 0.0
        assert resp.items[0].description is None
        assert resp.items[0].is_active is False

    def test_custom_page_params_propagate(self):
        session = _make_session(items=[], total=0)
        resp = report_services(db=session, clinic_id=1, page=3, size=5)
        assert resp.page == 3
        assert resp.size == 5


# ---------------------------------------------------------------------------
# Tests: aislamiento por clínica (tenant isolation)
# ---------------------------------------------------------------------------


class TestReportServicesClinicIsolation:
    def test_data_separated_by_clinic(self):
        session_1 = _make_session(
            items=[_make_service(id=100, clinic_id=1)], total=1
        )
        session_2 = _make_session(items=[], total=0)

        resp_1 = report_services(db=session_1, clinic_id=1)
        resp_2 = report_services(db=session_2, clinic_id=2)

        assert resp_1.total == 1
        assert resp_1.items[0].clinic_id == 1
        assert resp_2.total == 0
        session_1.query.return_value.filter.assert_called()
        session_2.query.return_value.filter.assert_called()


# ---------------------------------------------------------------------------
# Tests: filtro por rango de fechas
# ---------------------------------------------------------------------------


class TestReportServicesPeriodFilter:
    @pytest.fixture()
    def period_start(self) -> datetime:
        return datetime(2025, 1, 1, tzinfo=UTC)

    @pytest.fixture()
    def period_end(self) -> datetime:
        return datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)

    def test_with_full_period(self, period_start, period_end):
        items = [
            _make_service(
                id=i + 1, clinic_id=1,
                created=datetime(2025, 1, i + 5, tzinfo=UTC),
            )
            for i in range(5)
        ]
        session = _make_session(items=items, total=5)
        resp = report_services(
            db=session, clinic_id=1,
            period_start=period_start, period_end=period_end,
        )
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 5
        assert len(resp.items) == 5

    def test_period_start_only(self, period_start):
        session = _make_session(items=[], total=0)
        resp = report_services(
            db=session, clinic_id=1, period_start=period_start
        )
        assert isinstance(resp, PaginatedResponse)

    def test_period_does_not_break_pagination(self, period_start, period_end):
        all_items = [
            _make_service(
                id=i + 1, clinic_id=1,
                created=datetime(2025, 1, i + 5, tzinfo=UTC),
            )
            for i in range(7)
        ]
        session = _make_session(items=all_items, total=7)
        resp = report_services(
            db=session, clinic_id=1,
            period_start=period_start, period_end=period_end,
        )
        assert resp.total == 7
        assert len(resp.items) == 7
        assert resp.page == 1
        assert resp.size == 20


# ---------------------------------------------------------------------------
# Tests: sin persistencia (solo lectura)
# ---------------------------------------------------------------------------


class TestReportServicesNoPersistence:
    def test_no_write_side_effects(self):
        session = _make_session(items=[], total=0)
        report_services(db=session, clinic_id=1)
        session.add.assert_not_called()
        session.flush.assert_not_called()
        session.delete.assert_not_called()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()

    def test_no_new_records_even_with_data(self):
        items = [_make_service(id=i + 1, clinic_id=1) for i in range(3)]
        session = _make_session(items=items, total=3)
        before_len = len(items)
        resp = report_services(db=session, clinic_id=1)
        assert len(items) == before_len  # no se agregó nada
        assert resp.total == 3
        session.add.assert_not_called()
        session.commit.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: ordenamiento determinista (QA-015 regression)
# ---------------------------------------------------------------------------


class TestReportServicesDeterministicOrdering:
    """Bloquea el defecto de paginación no determinista observado en QA-015.

    Con ``ORDER BY name ASC`` sin tiebreaker, dos ``Service`` con el mismo
    ``name`` pueden intercambiarse de posición entre una y otra petición,
    produciendo *overlap* / *missing rows* entre páginas.

    La solución: ``order_by(name.asc(), id.asc())``.
    """

    def test_order_by_uses_name_then_id(self):
        from app.infrastructure.database.models.service_model import Service

        session = _make_session(items=[], total=0)
        report_services(db=session, clinic_id=1)
        args = session.query.return_value.filter.return_value.order_by.call_args_list[-1].args
        assert len(args) == 2, (
            "report_services debe ordenar por name + id "
            "para una paginación estable (QA-015)"
        )
        assert str(args[0]) == str(Service.name.asc())
        assert str(args[1]) == str(Service.id.asc())
