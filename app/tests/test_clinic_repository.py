import pytest
from unittest.mock import Mock, patch
from app.infrastructure.repositories.clinic_repository_impl import ClinicRepositoryImpl

def test_get_branch_profile_success():
    # Mock database session
    mock_db = Mock()
    
    # Setup mock data
    clinic_branch = Mock()
    clinic_branch.id = 1
    clinic_branch.name = "Test Branch"
    clinic_branch.address = "Test Address"
    clinic_branch.phone = "123-456-7890"
    clinic_branch.email = "test@example.com"
    clinic_branch.is_available = True
    
    schedule1 = Mock()
    schedule1.day_of_week = "Monday"
    schedule1.open_time = "09:00"
    schedule1.close_time = "17:00"
    
    schedule2 = Mock()
    schedule2.day_of_week = "Tuesday"  
    schedule2.open_time = "09:00"
    schedule2.close_time = "17:00"
    
    service1 = Mock()
    service1.id = 1
    service1.name = "Vaccination"
    service1.description = "Vaccination services"
    service1.duration_minutes = 30
    
    service2 = Mock()
    service2.id = 2
    service2.name = "Checkup"
    service2.description = "General checkup"
    service2.duration_minutes = 45
    
    mock_db.query.return_value.filter.return_value.first.return_value = clinic_branch
    mock_db.query.return_value.filter.return_value.all.return_value = [schedule1, schedule2]
    
    # Test the repository method
    repo = ClinicRepositoryImpl(mock_db)
    result = repo.get_branch_profile(1)
    
    assert result['id'] == 1
    assert result['name'] == "Test Branch"
    assert len(result['schedules']) == 2
    assert len(result['services']) == 0

def test_get_clinic_branch_profile_access_check():
    # Mock database session  
    mock_db = Mock()
    
    clinic_branch = Mock()
    clinic_branch.id = 1
    clinic_branch.clinic_id = 1
    
    mock_db.query.return_value.filter.return_value.first.return_value = clinic_branch
    
    repo = ClinicRepositoryImpl(mock_db)
    
    # This should not raise an error when branch belongs to clinic
    result = repo.get_clinic_branch_profile(1, 1)
    
    assert result['id'] == 1
    assert result['clinic_name'] == "Clinic 1"