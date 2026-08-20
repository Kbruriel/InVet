
"""Integration tests for consultation API endpoints (BE-009)."""

from unittest.mock import AsyncMock, MagicMock
import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

import app.api.v1.routers.consultation_router as consultation_router_mod
from app.api.v1.routers.consultation_router import router
from app.domain.entities.consultation import Consultation


@pytest_asyncio.fixture
async def consultation_app():
    """Create a FastAPI app with consultation routes and dependency overrides."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/v1")

    # Consultation + Appointment repositories are async (awaited by use cases).
    # PetRepository is sync per the domain ABC.
    mock_consultation_repo = AsyncMock()
    mock_appointment_repo = AsyncMock()
    mock_pet_repo = MagicMock()
    mock_owner_repo = MagicMock()

    def get_mock_consultation_repo():
        return mock_consultation_repo

    def get_mock_appointment_repo():
        return mock_appointment_repo

    def get_mock_pet_repo():
        return mock_pet_repo

    def get_mock_owner_repo():
        return mock_owner_repo

    async def get_mock_db():
        class FakeSession:
            def close(self):
                pass
        yield FakeSession()

    async def get_mock_user():
        return {"user_id": 1, "clinic_id": 1, "role": "veterinarian"}

    test_app.dependency_overrides[consultation_router_mod.get_consultation_repo] = get_mock_consultation_repo
    test_app.dependency_overrides[consultation_router_mod.get_appointment_repo] = get_mock_appointment_repo
    test_app.dependency_overrides[consultation_router_mod.get_pet_repo] = get_mock_pet_repo
    test_app.dependency_overrides[consultation_router_mod.get_owner_repo] = get_mock_owner_repo
    test_app.dependency_overrides[consultation_router_mod.get_current_db] = get_mock_db
    test_app.dependency_overrides[consultation_router_mod.get_current_access_user] = get_mock_user

    yield {
        "app": test_app,
        "mock_consultation_repo": mock_consultation_repo,
        "mock_appointment_repo": mock_appointment_repo,
        "mock_pet_repo": mock_pet_repo,
        "mock_owner_repo": mock_owner_repo,
    }

    test_app.dependency_overrides.clear()


class TestCreateConsultationAPI:
    @pytest.mark.asyncio
    async def test_create_consultation_api(self, consultation_app):
        # Arrange
        test_app = consultation_app["app"]
        mock_consultation_repo = consultation_app["mock_consultation_repo"]
        mock_appointment_repo = consultation_app["mock_appointment_repo"]
        mock_pet_repo = consultation_app["mock_pet_repo"]

        from app.domain.entities.appointment import Appointment, AppointmentStatus, AppointmentType
        from datetime import datetime, timedelta

        appointment = Appointment(
            id=1, 
            owner_id=1,
            pet_id=1, 
            clinic_id=1, 
            branch_id=1,
            appointment_type=AppointmentType.CONSULTATION,
            scheduled_start=datetime.now(),
            scheduled_end=datetime.now() + timedelta(minutes=30),
            status=AppointmentStatus.COMPLETED
        )
        mock_appointment_repo.get_by_id.return_value = appointment
        
        mock_pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=1)

        consultation_data = {
            "appointment_id": 1,
            "pet_id": 1,
            "branch_id": 1,
            "veterinarian_id": 1,
            "history": "test history",
            "diagnosis": "test diagnosis",
            "recommendations": "test recommendations",
        }
        
        consultation_result = Consultation(
            id=1, appointment_id=1, pet_id=1, clinic_id=1, branch_id=1, 
            history="...", diagnosis="...", recommendations="..."
        )
        mock_consultation_repo.get_by_appointment_id.return_value = None
        mock_consultation_repo.create_consultation.return_value = consultation_result

        # Act
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            response = await ac.post("/api/v1/consultations", json=consultation_data)

        # Assert
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_consultation_api_derives_optional_fields(self, consultation_app):
        test_app = consultation_app["app"]
        mock_consultation_repo = consultation_app["mock_consultation_repo"]
        mock_appointment_repo = consultation_app["mock_appointment_repo"]
        mock_pet_repo = consultation_app["mock_pet_repo"]

        from app.domain.entities.appointment import Appointment, AppointmentStatus, AppointmentType
        from datetime import datetime, timedelta

        appointment = Appointment(
            id=2,
            owner_id=1,
            pet_id=1,
            clinic_id=1,
            branch_id=7,
            appointment_type=AppointmentType.CONSULTATION,
            scheduled_start=datetime.now(),
            scheduled_end=datetime.now() + timedelta(minutes=30),
            status=AppointmentStatus.COMPLETED,
        )
        mock_appointment_repo.get_by_id.return_value = appointment
        mock_pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=1)
        mock_consultation_repo.get_by_appointment_id.return_value = None
        mock_consultation_repo.create_consultation.return_value = Consultation(
            id=2,
            appointment_id=2,
            pet_id=1,
            clinic_id=1,
            branch_id=7,
            history="",
            diagnosis="diagnosis only",
            recommendations="",
        )

        consultation_data = {
            "appointment_id": 2,
            "pet_id": 1,
            "diagnosis": "diagnosis only",
        }

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            response = await ac.post("/api/v1/consultations", json=consultation_data)

        assert response.status_code == 201
        assert response.json()["branch_id"] == 7
        assert response.json()["history"] == ""
        assert response.json()["recommendations"] == ""


class TestConsultationReadAndListAccess:
    @pytest.mark.asyncio
    async def test_owner_can_read_own_consultation(self, consultation_app):
        test_app = consultation_app["app"]
        mock_consultation_repo = consultation_app["mock_consultation_repo"]
        mock_pet_repo = consultation_app["mock_pet_repo"]
        mock_owner_repo = consultation_app["mock_owner_repo"]

        async def get_owner_user():
            return {"user_id": 10, "clinic_id": 1, "role": "user"}

        test_app.dependency_overrides[consultation_router_mod.get_current_access_user] = get_owner_user
        mock_owner_repo.get_owner_by_user_id.return_value = MagicMock(id=55)
        mock_pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=55)
        mock_consultation_repo.get_by_id.return_value = Consultation(
            id=10,
            appointment_id=1,
            pet_id=33,
            clinic_id=1,
            branch_id=1,
            history="historia",
            diagnosis="diagnosis",
            recommendations="recommendations",
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            response = await ac.get("/api/v1/consultations/10")

        assert response.status_code == 200
        assert response.json()["id"] == 10

    @pytest.mark.asyncio
    async def test_owner_cannot_read_foreign_consultation(self, consultation_app):
        test_app = consultation_app["app"]
        mock_consultation_repo = consultation_app["mock_consultation_repo"]
        mock_pet_repo = consultation_app["mock_pet_repo"]
        mock_owner_repo = consultation_app["mock_owner_repo"]

        async def get_owner_user():
            return {"user_id": 10, "clinic_id": 1, "role": "user"}

        test_app.dependency_overrides[consultation_router_mod.get_current_access_user] = get_owner_user
        mock_owner_repo.get_owner_by_user_id.return_value = MagicMock(id=55)
        mock_pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=999)
        mock_consultation_repo.get_by_id.return_value = Consultation(
            id=11,
            appointment_id=1,
            pet_id=34,
            clinic_id=1,
            branch_id=1,
            history="historia",
            diagnosis="diagnosis",
            recommendations="recommendations",
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            response = await ac.get("/api/v1/consultations/11")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_owner_lists_only_own_pet_consultations(self, consultation_app):
        test_app = consultation_app["app"]
        mock_consultation_repo = consultation_app["mock_consultation_repo"]
        mock_pet_repo = consultation_app["mock_pet_repo"]
        mock_owner_repo = consultation_app["mock_owner_repo"]

        async def get_owner_user():
            return {"user_id": 10, "clinic_id": 1, "role": "user"}

        test_app.dependency_overrides[consultation_router_mod.get_current_access_user] = get_owner_user
        mock_owner_repo.get_owner_by_user_id.return_value = MagicMock(id=55)
        mock_pet_repo.get_pet_by_id.return_value = MagicMock(owner_id=55)
        mock_consultation_repo.list_by_pet.return_value = (
            [
                Consultation(
                    id=21,
                    appointment_id=1,
                    pet_id=33,
                    clinic_id=1,
                    branch_id=1,
                    history="historia",
                    diagnosis="diagnosis",
                    recommendations="recommendations",
                )
            ],
            1,
        )

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=test_app), base_url="http://test"
        ) as ac:
            response = await ac.get("/api/v1/consultations?pet_id=33")

        assert response.status_code == 200
        assert response.json()["meta"]["total"] == 1
        assert response.json()["items"][0]["id"] == 21
