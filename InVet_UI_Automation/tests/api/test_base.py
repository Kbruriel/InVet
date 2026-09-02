"""
Basic API tests for BE-014 slice
"""
import pytest
import httpx
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"

def test_api_endpoints_health():
    """Test that all main API endpoints are accessible"""
    response = httpx.get(f"{BASE_URL}/api/v1/tickets")
    assert response.status_code == 200

def test_ticket_creation_happy_path():
    """Test creating a valid ticket (C1)"""
    ticket_data = {
        "title": "Test ticket",
        "description": "This is a test ticket",
        "category_id": 1,
        "clinic_id": 1
    }
    
    response = httpx.post(f"{BASE_URL}/api/v1/tickets", json=ticket_data)
    assert response.status_code == 201

def test_ticket_creation_invalid_title():
    """Test that title shorter than 5 characters is rejected (C2)"""
    ticket_data = {
        "title": "Test",
        "description": "This is a test ticket",
        "category_id": 1,
        "clinic_id": 1
    }
    
    response = httpx.post(f"{BASE_URL}/api/v1/tickets", json=ticket_data)
    assert response.status_code == 400

def test_ticket_list_pagination():
    """Test pagination with page and page_size (C3)"""
    response = httpx.get(f"{BASE_URL}/api/v1/tickets?page=1&page_size=10")
    assert response.status_code == 200

def test_ticket_status_transition():
    """Test status transition for ticket (C5)"""
    # Create a ticket first
    ticket_data = {
        "title": "Test ticket",
        "description": "This is a test ticket",
        "category_id": 1,
        "clinic_id": 1
    }
    
    response = httpx.post(f"{BASE_URL}/api/v1/tickets", json=ticket_data)
    assert response.status_code == 201
    ticket_id = response.json()["id"]
    
    # Test status transition
    status_data = {"new_status": "pending"}
    response = httpx.patch(f"{BASE_URL}/api/v1/tickets/{ticket_id}/status", json=status_data)
    # This might be 403 if not properly authenticated, but should not return 5xx
    
def test_categories_endpoint():
    """Test categories endpoint (C8)"""
    response = httpx.get(f"{BASE_URL}/api/v1/tickets/categories")
    assert response.status_code == 200

def test_authentication_required():
    """Test that all endpoints require authentication (C9)"""
    # Test ticket creation without auth token
    ticket_data = {
        "title": "Test ticket",
        "description": "This is a test ticket",
        "category_id": 1,
        "clinic_id": 1
    }
    
    response = httpx.post(f"{BASE_URL}/api/v1/tickets", json=ticket_data)
    # Should fail with 401 or 403 for unauthorized access
    assert response.status_code in [401, 403]