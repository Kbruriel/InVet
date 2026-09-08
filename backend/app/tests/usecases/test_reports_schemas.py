"""Tests unitarios para report_schemas (BE-015-T01)."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.api.v1.schemas.report_schemas import (
    AppointmentSummaryDto,
    ServiceSummaryDto,
)


@pytest.fixture()
def base_dt() -> datetime:
    return datetime.now(UTC)


# -------------------------------------------------------- #
# AppointmentSummaryDto                                    #
# -------------------------------------------------------- #


class TestAppointmentSummaryDto:
    def test_valid_payload(self, base_dt: datetime) -> None:
        dt = AppointmentSummaryDto.model_validate(
            {
                "id": 1,
                "clinic_id": 42,
                "pet_name": "Max",
                "owner_name": "Juan Perez",
                "veterinarian_name": "Dr. Lopez",
                "appointment_type": "consultation",
                "status": "completed",
                "scheduled_start": base_dt.isoformat(),
                "scheduled_end": base_dt.isoformat(),
            }
        )
        assert dt.clinic_id == 42

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            AppointmentSummaryDto.model_validate({})


# -------------------------------------------------------- #
# ServiceSummaryDto                                        #
# -------------------------------------------------------- #


class TestServiceSummaryDto:
    def test_valid_payload(self) -> None:
        dt = ServiceSummaryDto.model_validate(
            {
                "id": 10,
                "clinic_id": 42,
                "name": "Vacuna rabia",
                "description": "Rabies vaccine",
                "price": 50.0,
                "duration_minutes": 30,
                "is_active": True,
            }
        )
        assert dt.name == "Vacuna rabia"

    def test_description_optional(self) -> None:
        dt = ServiceSummaryDto.model_validate(
            {
                "id": 1,
                "clinic_id": 1,
                "name": "X",
                "description": None,
                "price": 1.0,
                "duration_minutes": 1,
                "is_active": False,
            }
        )
        assert dt.description is None
