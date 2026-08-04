import pytest
from unittest.mock import Mock, patch
from app.application.use_cases.clinic_use_case import ClinicUseCase
from app.infrastructure.repositories.clinic_repository_impl import ClinicRepositoryImpl

def test_clinic_use_case_get_branch_profile():
    # Mock the repository
    mock_repo = Mock(spec=ClinicRepositoryImpl)
    
    # Setup expected data
    expected_data = {
        "id": 1,
        "name": "Test Branch",
        "address": "Test Address", 
        "phone": "123-456-7890",
        "email": "test@example.com",
        "schedules": [
            {"day_of_week": "Monday", "open_time": "09:00", "close_time": "17:00"}
        ],
        "services": [],
        "rating_summary": {"average_rating": 4.5, "total_reviews": 120},
        "is_available": True
    }
    
    mock_repo.get_branch_profile.return_value = expected_data
    
    # Create use case
    use_case = ClinicUseCase(repository=mock_repo)
    
    # Test
    result = use_case.get_branch_profile(1)
    
    assert result == expected_data
    mock_repo.get_branch_profile.assert_called_once_with(1)

def test_clinic_use_case_get_clinic_branch_profile():
    # Mock the repository
    mock_repo = Mock(spec=ClinicRepositoryImpl)
    
    # Setup expected data
    expected_data = {
        "id": 1,
        "clinic_name": "Clinic 1",
        "branch": {
            "id": 1,
            "name": "Test Branch",
            "address": "Test Address",
            "phone": "123-456-7890", 
            "email": "test@example.com",
            "schedules": [
                {"day_of_week": "Monday", "open_time": "09:00", "close_time": "17:00"}
            ],
            "services": [],
            "rating_summary": {"average_rating": 4.5, "total_reviews": 120},
            "is_available": True
        }
    }
    
    mock_repo.get_clinic_branch_profile.return_value = expected_data
    
    # Create use case
    use_case = ClinicUseCase(repository=mock_repo)
    
    # Test 
    result = use_case.get_clinic_branch_profile(1, 1)
    
    assert result == expected_data
    mock_repo.get_clinic_branch_profile.assert_called_once_with(1, 1)

def test_clinic_use_case_get_branch_profile_not_found():
    # Mock the repository
    mock_repo = Mock(spec=ClinicRepositoryImpl)
    mock_repo.get_branch_profile.side_effect = ValueError("Branch not found")
    
    # Create use case
    use_case = ClinicUseCase(repository=mock_repo)
    
    # Test
    with pytest.raises(ValueError, match="Branch not found"):
        use_case.get_branch_profile(999)