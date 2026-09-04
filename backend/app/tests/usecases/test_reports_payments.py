"""Tests unitarios: pagos paginados (BE-015-T07).

Objetivo: verificar que ``report_payments``:
- filtra por ``clinic_id`` (tenant isolation)
- acepta rango de fechas opcional
- retorna paginación coherente
- convierte ``amount`` (cents int en DB) a moneda (float)
- no realiza escritura en la sesión
- devuelve ``PaymentSummaryDto`` por cada registro

Validacion:
    python -m pytest backend/app/tests/usecases/test_reports_payments.py -q
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from app.api.v1.schemas.report_schemas import (
    PaginatedResponse,
    PaymentSummaryDto,
)
from app.application.usecases.reports.report_payments import report_payments


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


def _make_payment(
    id: int,
    clinic_id: int,
    amount_cents: int = 2500,
    method: str = "cash",
    status: str = "paid",
    paid_at: datetime | None = None,
) -> Any:
    p: Any = MagicMock()
    p.id = id
    p.clinic_id = clinic_id
    p.appointment_id = id * 10
    p.service_id = id * 100
    p.amount = amount_cents
    p.method.value = method
    p.status.value = status
    p.paid_at = paid_at or datetime(2025, 6, 15, tzinfo=UTC)
    return p


class TestReportPaymentsStructure:
    def test_paginated_structure_empty(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_payments(db=session, clinic_id=1)
        assert isinstance(resp, PaginatedResponse)
        assert resp.items == []
        assert resp.total == 0
        assert resp.page == 1
        assert resp.size == 20

    def test_returns_dto_with_all_fields(self) -> None:
        item = _make_payment(
            id=1,
            clinic_id=42,
            amount_cents=2500,
            method="card",
            status="paid",
            paid_at=datetime(2025, 6, 1, 12, tzinfo=UTC),
        )
        session = _make_session(items=[item], total=1)
        resp = report_payments(db=session, clinic_id=42)
        assert resp.total == 1
        assert len(resp.items) == 1
        dto: PaymentSummaryDto = resp.items[0]
        assert isinstance(dto, PaymentSummaryDto)
        assert dto.id == 1
        assert dto.clinic_id == 42
        assert dto.appointment_id == 10
        assert dto.service_id == 100
        assert dto.amount == 25.0
        assert dto.payment_method == "card"
        assert dto.status == "paid"
        assert dto.paid_at == datetime(2025, 6, 1, 12, tzinfo=UTC).isoformat()

    def test_amount_converted_from_cents(self) -> None:
        item = _make_payment(id=1, clinic_id=1, amount_cents=5000)
        session = _make_session(items=[item], total=1)
        resp = report_payments(db=session, clinic_id=1)
        assert resp.items[0].amount == 50.0

    def test_custom_page_params_propagate(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_payments(db=session, clinic_id=1, page=3, size=5)
        assert resp.page == 3
        assert resp.size == 5


class TestReportPaymentsClinicIsolation:
    def test_filter_applied(self) -> None:
        session = _make_session(items=[], total=0)
        report_payments(db=session, clinic_id=1)
        session.query.return_value.filter.assert_called()

    def test_two_clinics_independent(self) -> None:
        s1 = _make_session(items=[_make_payment(id=1, clinic_id=1)], total=1)
        s2 = _make_session(items=[], total=0)
        r1 = report_payments(db=s1, clinic_id=1)
        r2 = report_payments(db=s2, clinic_id=2)
        assert r1.total == 1
        assert r2.total == 0


class TestReportPaymentsPeriodFilter:
    def test_full_period(self) -> None:
        items = [_make_payment(id=i + 1, clinic_id=1) for i in range(5)]
        session = _make_session(items=items, total=5)
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 12, 31, tzinfo=UTC)
        resp = report_payments(
            db=session,
            clinic_id=1,
            period_start=start,
            period_end=end,
        )
        assert isinstance(resp, PaginatedResponse)
        assert resp.total == 5
        assert len(resp.items) == 5

    def test_start_only(self) -> None:
        session = _make_session(items=[], total=0)
        resp = report_payments(
            db=session,
            clinic_id=1,
            period_start=datetime(2025, 1, 1, tzinfo=UTC),
        )
        assert isinstance(resp, PaginatedResponse)

    def test_pagination_invariant(self) -> None:
        items = [_make_payment(id=i + 1, clinic_id=1) for i in range(7)]
        session = _make_session(items=items, total=7)
        resp = report_payments(
            db=session,
            clinic_id=1,
            period_start=datetime(2025, 1, 1, tzinfo=UTC),
            period_end=datetime(2025, 12, 31, tzinfo=UTC),
        )
        assert resp.total == 7
        assert len(resp.items) == 7
        assert resp.page == 1
        assert resp.size == 20


class TestReportPaymentsNoPersistence:
    def test_no_write_side_effects(self) -> None:
        session = _make_session(items=[], total=0)
        report_payments(db=session, clinic_id=1)
        session.add.assert_not_called()
        session.flush.assert_not_called()
        session.delete.assert_not_called()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: ordenamiento determinista (QA-015 regression)
# ---------------------------------------------------------------------------


class TestReportPaymentsDeterministicOrdering:
    """Bloquea el defecto de paginación no determinista observado en QA-015.

    Con ``ORDER BY paid_at DESC`` sin tiebreaker, dos ``Payment`` con el
    mismo ``paid_at`` pueden intercambiarse de posición entre una y otra
    petición, produciendo *overlap* / *missing rows* entre páginas.

    La solución: ``order_by(paid_at.desc(), id.desc())``.
    """

    def test_order_by_uses_paid_at_then_id(self) -> None:
        from app.infrastructure.database.models.payment import Payment

        session = _make_session(items=[], total=0)
        report_payments(db=session, clinic_id=1)
        args = session.query.return_value.filter.return_value.order_by.call_args_list[-1].args
        assert len(args) == 2, (
            "report_payments debe ordenar por paid_at + id "
            "para una paginación estable (QA-015)"
        )
        assert str(args[0]) == str(Payment.paid_at.desc())
        assert str(args[1]) == str(Payment.id.desc())
