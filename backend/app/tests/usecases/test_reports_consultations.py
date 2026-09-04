"""Tests unitarios: consultas medicas paginadas (BE-015-T05).

Objetivo: verificar que ``report_consultations``:
- filtra por ``clinic_id`` (tenant isolation)
- acepta rango de fechas opcional
- retorna paginación coherente
- no realiza escritura en la sesión
- devuelve ``ConsultationSummaryDto`` por cada registro

Validacion:
    python -m pytest backend/app/tests/usecases/test_reports_consultations.py -q
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from app.api.v1.schemas.report_schemas import (
    ConsultationSummaryDto,
    PaginatedResponse,
)
from app.application.usecases.reports.report_consultations import (
    report_consultations,
)


def _make_session(items: list[Any] | None = None, total: int = 0) -> MagicMock:
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


def _make_consultation(
    id: int,
    clinic_id: int,
    diagnosis: str = "Gastritis",
    history: str = "Malestar",
    recommendations: str = "Diet",
) -> Any:
    c: Any = MagicMock()
    c.id = id
    c.clinic_id = clinic_id
    c.diagnosis = diagnosis
    c.history = history
    c.recommendations = recommendations
    c.updated_at = datetime(2025, 6, 15, tzinfo=UTC)
    c.created_at = datetime(2025, 6, 1, tzinfo=UTC)
    return c


class TestReportConsultationsStructure:
    def test_paginated_structure_empty(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_consultations(db=session, clinic_id=1)
        assert isinstance(resp, PaginatedResponse)
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.size == 20

    def test_returns_dto_with_core_fields(self) -> None:
        item = _make_consultation(
            id=10,
            clinic_id=42,
            diagnosis="Diabetes",
            history="Polidipsia",
            recommendations="Insulina",
        )
        session = _make_session(items=[item], total=1)
        resp = report_consultations(db=session, clinic_id=42)
        assert resp.total == 1
        assert len(resp.items) == 1
        dto: ConsultationSummaryDto = resp.items[0]
        assert isinstance(dto, ConsultationSummaryDto)
        assert dto.id == 10
        assert dto.clinic_id == 42
        assert dto.diagnosis == "Diabetes"
        assert dto.history == "Polidipsia"
        assert dto.recommendations == "Insulina"

    def test_custom_page_params_propagate(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_consultations(db=session, clinic_id=1, page=3, size=5)
        assert resp.page == 3
        assert resp.size == 5


class TestReportConsultationsClinicIsolation:
    def test_filter_applied(self) -> None:
        session = _make_session(items=[], total=0)
        report_consultations(db=session, clinic_id=1)
        session.query.return_value.filter.assert_called()

    def test_two_clinics_independent(self) -> None:
        s1 = _make_session(
            items=[_make_consultation(id=1, clinic_id=1)], total=1
        )
        s2 = _make_session(items=[], total=0)
        r1 = report_consultations(db=s1, clinic_id=1)
        r2 = report_consultations(db=s2, clinic_id=2)
        assert r1.total == 1
        assert r2.total == 0


class TestReportConsultationsPeriodFilter:
    def test_full_period(self) -> None:
        items = [
            _make_consultation(id=i + 1, clinic_id=1) for i in range(4)
        ]
        session = _make_session(items=items, total=4)
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 12, 31, tzinfo=UTC)
        resp = report_consultations(
            db=session,
            clinic_id=1,
            period_start=start,
            period_end=end,
        )
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 4
        assert len(resp.items) == 4

    def test_start_only(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_consultations(
            db=session,
            clinic_id=1,
            period_start=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert isinstance(resp, PaginatedResponse)

    def test_pagination_invariant_with_period(self) -> None:
        items = [_make_consultation(id=i + 1, clinic_id=1) for i in range(6)]
        session = _make_session(items=items, total=6)
        resp = report_consultations(
            db=session,
            clinic_id=1,
            period_start=datetime(2025, 1, 1, tzinfo=UTC),
            period_end=datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert resp.total == 6
        assert len(resp.items) == 6
        assert resp.page == 1
        assert resp.size == 20


class TestReportConsultationsNoPersistence:
    def test_no_write_side_effects(self) -> None:
        session = _make_session(items=[], total=0)
        report_consultations(db=session, clinic_id=1)
        session.add.assert_not_called()
        session.flush.assert_not_called()
        session.delete.assert_not_called()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: ordenamiento determinista (QA-015 regression)
# ---------------------------------------------------------------------------


class TestReportConsultationsDeterministicOrdering:
    """Bloquea el defecto de paginación no determinista observado en QA-015.

    Con ``ORDER BY updated_at DESC`` sin tiebreaker, dos ``Consultation``
    con el mismo ``updated_at`` pueden intercambiarse de posición entre una
    y otra petición, produciendo *overlap* / *missing rows* entre páginas.

    La solución: ``order_by(updated_at.desc(), id.desc())``.
    """

    def test_order_by_uses_updated_at_then_id(self) -> None:
        from app.infrastructure.database.models.consultation import Consultation

        session = _make_session(items=[], total=0)
        report_consultations(db=session, clinic_id=1)
        args = session.query.return_value.filter.return_value.order_by.call_args_list[-1].args
        assert len(args) == 2, (
            "report_consultations debe ordenar por updated_at + id "
            "para una paginación estable (QA-015)"
        )
        assert str(args[0]) == str(Consultation.updated_at.desc())
        assert str(args[1]) == str(Consultation.id.desc())
