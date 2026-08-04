import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.application.use_cases.get_branch_public_profile import GetBranchPublicProfileUseCase
from app.domain.entities.branch import BranchProfile

client = TestClient(app)

@pytest.fixture
def mock_use_case():
    return AsyncMock(spec=GetBranchPublicProfileUseCase)

@pytest.mark.asyncio
async def test_get_branch_public_profile_success(mock_use_case):
    # Arrange
    branch_id = 1
    expected_profile = BranchProfile(
        id=1,
        name="Test Clinic",
        address="123 Main St",
        phone="555-1234",
        email="test@example.com",
        schedules=[],
        services=[],
        rating_summary={"average_rating": 4.5, "total_reviews": 10},
        is_available=True
    )
    
    mock_use_case.execute.return_value = expected_profile

    # Act
    response = client.get(f"/api/v1/clinics/branches/{branch_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "Test Clinic"

@pytest.mark.asyncio
async def test_get_branch_public_profile_not_found(mock_use_case):
    # Arrange
    branch_id = 999
    mock_use_case.execute.side_effect = Exception("Branch not found")

    # Act
    response = client.get(f"/api/v1/clinics/branches/{branch_id}")

    # Assert
    assert response.status_code == 404
