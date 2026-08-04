"""Pruebas para los perfiles de clínica/sucursal."""
from datetime import datetime, time
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.use_cases.branch_profile import (
    GetBranchProtectedProfileUseCase,
    GetBranchPublicProfileUseCase,
)
from app.domain.entities.branch import (
    AvailabilitySummary,
    Branch,
    BranchSchedule,
    RatingSummary,
    Service,
)


class TestBranchProfileUseCases:
    """Test para casos de uso del perfil de clínica/sucursal."""

    @pytest.mark.asyncio
    async def test_get_branch_public_profile_use_case(self):
        """Prueba del caso de uso de perfil público."""
        branch_repo = Mock()
        service_repo = Mock()
        schedule_repo = Mock()
        rating_repo = Mock()
        availability_repo = Mock()

        branch_repo.get_branch_public_profile = AsyncMock(return_value=Branch(
            id=1,
            clinic_id=1,
            name="Clinica Test",
            description="Descripción de prueba",
            address="Calle 123",
            city="Ciudad Test",
            state="Estado Test",
            country="País Test",
            postal_code="12345",
            phone="123-456-7890",
            email="test@example.com",
            is_active=True,
            created_at=datetime(2023, 1, 1, 0, 0, 0),
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ))

        service_repo.get_services_by_branch = AsyncMock(return_value=[
            Service(
                id=1,
                branch_id=1,
                name="Servicio de prueba",
                description="Descripción del servicio",
                is_active=True,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
            )
        ])

        schedule_repo.get_schedules_by_branch = AsyncMock(return_value=[
            BranchSchedule(
                id=1,
                branch_id=1,
                day_of_week=1,
                open_time="09:00",
                close_time="18:00",
                is_active=True,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
            )
        ])

        rating_repo.get_rating_summary_by_branch = AsyncMock(return_value=RatingSummary(
            id=1,
            branch_id=1,
            average_rating=4.5,
            total_reviews=100,
            review_distribution=None,
            created_at=datetime(2023, 1, 1, 0, 0, 0),
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ))

        availability_repo.get_availability_summary_by_branch = AsyncMock(return_value=AvailabilitySummary(
            id=1,
            branch_id=1,
            is_available=True,
            next_available_time=None,
            availability_type="full",
            created_at=datetime(2023, 1, 1, 0, 0, 0),
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ))

        use_case = GetBranchPublicProfileUseCase(
            branch_repo, service_repo, schedule_repo, rating_repo, availability_repo
        )

        result = await use_case.execute(1)

        assert result is not None
        assert result.id == 1
        assert len(result.services) == 1
        assert len(result.schedules) == 1
        assert result.rating_summary is not None
        assert result.availability_summary is not None

    @pytest.mark.asyncio
    async def test_get_branch_protected_profile_use_case(self):
        """Prueba del caso de uso de perfil protegido."""
        branch_repo = Mock()
        service_repo = Mock()
        schedule_repo = Mock()
        rating_repo = Mock()
        availability_repo = Mock()
        current_user = {
            "id": 7,
            "email": "owner@example.com",
            "role": "user",
        }

        branch_repo.is_branch_accessible = AsyncMock(return_value=True)
        branch_repo.get_branch_protected_profile = AsyncMock(return_value=Branch(
            id=1,
            clinic_id=1,
            name="Clinica Test",
            description="Descripción de prueba",
            address="Calle 123",
            city="Ciudad Test",
            state="Estado Test",
            country="País Test",
            postal_code="12345",
            phone="123-456-7890",
            email="test@example.com",
            is_active=True,
            created_at=datetime(2023, 1, 1, 0, 0, 0),
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ))

        service_repo.get_services_by_branch = AsyncMock(return_value=[
            Service(
                id=1,
                branch_id=1,
                name="Servicio de prueba",
                description="Descripción del servicio",
                is_active=True,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
            )
        ])

        schedule_repo.get_schedules_by_branch = AsyncMock(return_value=[
            BranchSchedule(
                id=1,
                branch_id=1,
                day_of_week=1,
                open_time="09:00",
                close_time="18:00",
                is_active=True,
                created_at=datetime(2023, 1, 1, 0, 0, 0),
                updated_at=datetime(2023, 1, 1, 0, 0, 0),
            )
        ])

        rating_repo.get_rating_summary_by_branch = AsyncMock(return_value=RatingSummary(
            id=1,
            branch_id=1,
            average_rating=4.5,
            total_reviews=100,
            review_distribution=None,
            created_at=datetime(2023, 1, 1, 0, 0, 0),
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ))

        availability_repo.get_availability_summary_by_branch = AsyncMock(return_value=AvailabilitySummary(
            id=1,
            branch_id=1,
            is_available=True,
            next_available_time=None,
            availability_type="full",
            created_at=datetime(2023, 1, 1, 0, 0, 0),
            updated_at=datetime(2023, 1, 1, 0, 0, 0),
        ))

        use_case = GetBranchProtectedProfileUseCase(
            branch_repo, service_repo, schedule_repo, rating_repo, availability_repo
        )

        result = await use_case.execute(1, 1, current_user)

        assert result is not None
        assert result.id == 1
        assert len(result.services) == 1
        assert len(result.schedules) == 1
        assert result.rating_summary is not None
        assert result.availability_summary is not None

    @pytest.mark.asyncio
    async def test_get_branch_protected_profile_denies_unauthorized_user(self):
        """Prueba que el caso de uso niega acceso sin ownership."""
        branch_repo = Mock()
        service_repo = Mock()
        schedule_repo = Mock()
        rating_repo = Mock()
        availability_repo = Mock()

        branch_repo.is_branch_accessible = AsyncMock(return_value=False)
        branch_repo.get_branch_protected_profile = AsyncMock()

        use_case = GetBranchProtectedProfileUseCase(
            branch_repo, service_repo, schedule_repo, rating_repo, availability_repo
        )

        result = await use_case.execute(
            1,
            1,
            {"id": 8, "email": "intruder@example.com", "role": "user"},
        )

        assert result is None
        branch_repo.get_branch_protected_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_branch_not_found(self):
        """Prueba cuando no se encuentra la sucursal."""
        branch_repo = Mock()

        branch_repo.get_branch_public_profile = AsyncMock(return_value=None)

        use_case = GetBranchPublicProfileUseCase(
            branch_repo, Mock(), Mock(), Mock(), Mock()
        )

        result = await use_case.execute(999)

        assert result is None
