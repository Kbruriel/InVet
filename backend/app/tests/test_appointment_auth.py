"""Tests para autenticación y autorización de citas (AC-008-01, AC-008-02)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.app import app
from app.infrastructure.database.session import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    return TestClient(app)


def test_get_appointment_unauthenticated(client):
    """Sin autenticación, GET retorna 401."""
    response = client.get("/api/v1/appointments/1")
    assert response.status_code == 401


def test_list_appointments_unauthenticated(client):
    """Sin autenticación, LIST retorna 401."""
    response = client.get("/api/v1/appointments")
    assert response.status_code == 401


def test_create_appointment_unauthenticated(client):
    """Sin autenticación, POST retorna 401."""
    response = client.post(
        "/api/v1/appointments",
        json={
            "owner_id": 1,
            "scheduled_start": "2026-12-31T10:00:00",
            "scheduled_end": "2026-12-31T10:30:00",
        },
    )
    assert response.status_code == 401


def test_update_appointment_unauthenticated(client):
    """Sin autenticación, PUT retorna 401."""
    response = client.put("/api/v1/appointments/1", json={"reason": "test"})
    assert response.status_code == 401


def test_transition_status_unauthenticated(client):
    """Sin autenticación, POST status retorna 401."""
    response = client.post("/api/v1/appointments/1/status", json={"status": "approved"})
    assert response.status_code == 401


def test_delete_appointment_unauthenticated(client):
    """Sin autenticación, DELETE retorna 401."""
    response = client.delete("/api/v1/appointments/1")
    assert response.status_code == 401


def test_availability_unauthenticated(client):
    """Sin autenticación, GET availability retorna 401."""
    response = client.get("/api/v1/appointments/availability?date=2026-12-31")
    assert response.status_code == 401
