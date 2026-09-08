"""Tests unitarios: resumen de ratings por clinica (BE-015-T06).

Objetivo: verificar que ``report_ratings_summary``:
- filtra por ``clinic_id`` vía Branch (tenant isolation)
- acepta rango de fechas opcional
- retorna paginación coherente
- no realiza escritura en la sesión
- devuelve ``RatingSummaryDto`` por cada registro

Validacion:
    python -m pytest backend/app/tests/usecases/test_reports_ratings_summary.py -q
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from app.api.v1.schemas.report_schemas import (
    PaginatedResponse,
    RatingSummaryDto,
)
from app.application.usecases.reports.report_ratings_summary import (
    report_ratings_summary,
)


def _make_session(items: list[Any] | None = None, total: int = 0) -> MagicMock:
    session: Any = MagicMock()
    query: Any = MagicMock()

    query.join.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.offset.return_value = query
    query.limit.return_value = query
    query.count.return_value = total
    query.all.return_value = items or []

    session.query.return_value.join.return_value = query
    return session


def _make_rating_tuple(rs: Any, branch: Any) -> tuple[Any, Any]:
    return (rs, branch)


def _make_rating_summary(average_rating: float = 4.5, total_reviews: int = 80) -> Any:
    rs: Any = MagicMock()
    rs.average_rating = average_rating
    rs.total_reviews = total_reviews
    rs.created_at = datetime(2025, 6, 15, tzinfo=UTC)
    rs.updated_at = datetime(2025, 6, 15, tzinfo=UTC)
    rs.branch_id = 1
    return rs


def _make_branch() -> Any:
    branch: Any = MagicMock()
    branch.id = 1
    branch.clinic_id = 42
    return branch


class TestReportRatingsSummaryStructure:
    def test_paginated_structure_empty(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_ratings_summary(db=session, clinic_id=42)
        assert isinstance(resp, PaginatedResponse)
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.size == 20

    def test_returns_dto_with_core_fields(self) -> None:
        pairs = [
            _make_rating_tuple(_make_rating_summary(4.5, 80), _make_branch()),
            _make_rating_tuple(_make_rating_summary(3.0, 12), _make_branch()),
        ]
        session = _make_session(items=pairs, total=2)
        resp = report_ratings_summary(db=session, clinic_id=42)
        assert resp.total == 2
        assert len(resp.items) == 2
        first: RatingSummaryDto = resp.items[0]
        assert isinstance(first, RatingSummaryDto)
        assert first.average_rating == 4.5
        assert first.total_reviews == 80
        # veterinarian_id no se resuelve en este modelo
        assert first.veterinarian_id is None

    def test_null_average_and_total(self) -> None:
        rs = _make_rating_summary(None, None)  # type: ignore[arg-type]
        session = _make_session(items=[_make_rating_tuple(rs, _make_branch())], total=1)
        resp = report_ratings_summary(db=session, clinic_id=1)
        assert resp.items[0].average_rating == 0.0
        assert resp.items[0].total_reviews == 0

    def test_custom_page_params_propagate(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_ratings_summary(db=session, clinic_id=1, page=4, size=10)
        assert resp.page == 4
        assert resp.size == 10


class TestReportRatingsSummaryClinicIsolation:
    def test_join_and_filter_applied(self) -> None:
        session = _make_session(items=[], total=0)
        report_ratings_summary(db=session, clinic_id=7)
        session.query.return_value.join.assert_called()
        session.query.return_value.join.return_value.filter.assert_called()


class TestReportRatingsSummaryPeriodFilter:
    def test_full_period(self) -> None:
        pairs = [
            _make_rating_tuple(_make_rating_summary(), _make_branch()) for _ in range(3)
        ]
        session = _make_session(items=pairs, total=3)
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 12, 31, tzinfo=UTC)
        resp = report_ratings_summary(
            db=session,
            clinic_id=1,
            period_start=start,
            period_end=end,
        )
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 3
        assert len(resp.items) == 3

    def test_start_only(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_ratings_summary(
            db=session,
            clinic_id=1,
            period_start=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert isinstance(resp, PaginatedResponse)


class TestReportRatingsSummaryNoPersistence:
    def test_no_write_side_effects(self) -> None:
        session = _make_session(items=[], total=0)
        report_ratings_summary(db=session, clinic_id=1)
        session.add.assert_not_called()
        session.flush.assert_not_called()
        session.delete.assert_not_called()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: ordenamiento determinista (QA-015 regression)
# ---------------------------------------------------------------------------


class TestReportRatingsSummaryDeterministicOrdering:
    """Bloquea el defecto de paginación no determinista observado en QA-015.

    Con ``ORDER BY created_at DESC`` sin tiebreaker, dos ``RatingSummary``
    con el mismo ``created_at`` pueden intercambiarse de posición entre una
    y otra petición, produciendo *overlap* / *missing rows* entre páginas.

    La solución: ``order_by(created_at.desc(), id.desc())``.

    Este use-case encadena ``join()`` antes de ``order_by()``, por eso se
    aserciona sobre el mismo ``query`` (que es el retorno idempotente del
    mock de ``join()``) donde vive el ``order_by``.
    """

    def test_order_by_uses_created_at_then_id(self) -> None:
        from app.infrastructure.database.models.rating_summary import (
            RatingSummary,
        )

        session = _make_session(items=[], total=0)
        report_ratings_summary(db=session, clinic_id=1)
        order_by = session.query.return_value.join.return_value.order_by
        args = order_by.call_args_list[-1].args
        assert len(args) == 2, (
            "report_ratings_summary debe ordenar por created_at + id "
            "para una paginación estable (QA-015)"
        )
        assert str(args[0]) == str(RatingSummary.created_at.desc())
        assert str(args[1]) == str(RatingSummary.id.desc())
