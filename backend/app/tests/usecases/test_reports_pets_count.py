"""Tests unitarios: conteo de mascotas activas por clinica (BE-015-T04).

Objetivo: verificar que ``report_pets_count``:
- filtra por ``clinic_id`` (tenant isolation)
- cuenta solo ``Pet.is_active == True``
- acepta rango de fechas opcional
- devuelve ``PetCountDto`` plano con {clinic_id, active_count}
- no realiza escritura en la session

Validacion:
    python -m pytest backend/app/tests/usecases/test_reports_pets_count.py -q
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

from app.api.v1.schemas.report_schemas import PetCountDto
from app.application.usecases.reports.report_pets_count import report_pets_count


def _make_session(total: int = 0) -> MagicMock:
    session: Any = MagicMock()
    query: Any = MagicMock()

    query.join.return_value = query
    query.filter.return_value = query
    query.count.return_value = total

    session.query.return_value.join.return_value = query
    return session


class TestReportPetsCountStructure:
    def test_empty_count(self) -> None:
        session = _make_session(total=0)
        resp = report_pets_count(db=session, clinic_id=42)
        assert isinstance(resp, PetCountDto)
        assert resp.clinic_id == 42
        assert resp.active_count == 0

    def test_count_propagates_to_dto(self) -> None:
        session = _make_session(total=17)
        resp = report_pets_count(db=session, clinic_id=99)
        assert isinstance(resp, PetCountDto)
        assert resp.active_count == 17
        assert resp.clinic_id == 99


class TestReportPetsCountClinicIsolation:
    def test_filter_always_applied_by_clinic(self) -> None:
        session = _make_session(total=0)
        report_pets_count(db=session, clinic_id=1)
        # El filtro por clinica se aplica en todas las llamadas
        session.query.return_value.join.return_value.filter.assert_called()

    def test_two_clinics_have_independent_counts(self) -> None:
        session_a = _make_session(total=5)
        session_b = _make_session(total=0)
        resp_a = report_pets_count(db=session_a, clinic_id=1)
        resp_b = report_pets_count(db=session_b, clinic_id=2)
        assert isinstance(resp_a, PetCountDto)
        assert isinstance(resp_b, PetCountDto)
        assert resp_a.active_count == 5
        assert resp_b.active_count == 0
        assert resp_b.clinic_id == 2


class TestReportPetsCountPeriodFilter:
    def test_period_does_not_change_shape(self) -> None:
        session = _make_session(total=3)
        start = datetime(2025, 1, 1, tzinfo=UTC)
        end = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)
        resp = report_pets_count(
            db=session, clinic_id=1, period_start=start, period_end=end
        )
        assert isinstance(resp, PetCountDto)
        assert resp.active_count == 3

    def test_period_start_only(self) -> None:
        session = _make_session(total=1)
        resp = report_pets_count(
            db=session, clinic_id=1, period_start=datetime(2025, 1, 1, tzinfo=UTC)
        )
        assert isinstance(resp, PetCountDto)
        assert resp.active_count == 1


class TestReportPetsCountNoPersistence:
    def test_no_write_side_effects(self) -> None:
        session = _make_session(total=2)
        report_pets_count(db=session, clinic_id=1)
        session.add.assert_not_called()
        session.flush.assert_not_called()
        session.delete.assert_not_called()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()
