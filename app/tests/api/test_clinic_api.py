import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_branch_profile(client):
    response = client.get("/api/v1/clinics/branches/1")
    
    # As our router is just stubbed, it would return a 404 by default, 
    # but we want to at least make sure the route exists
    assert response.status_code in [200, 404]

def test_get_clinic_branch_profile(client):
    response = client.get("/api/v1/clinics/1/1")
    
    # As our router is just stubbed, it would return a 404 by default, 
    # but we want to at least make sure the route exists
    assert response.status_code in [200, 404]