"""Tests para la base de datos."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.user import User
from app.infrastructure.database.session import Base


@pytest.fixture(scope="session")
def test_engine():
    """Crea un motor de base de datos para prueba."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine):
    """Crea una sesión de base de datos para prueba."""
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    yield session
    session.close()


def test_user_model_creation(db_session):
    """Prueba la creación de modelo de usuario."""
    user = User(
        email="test@example.com", username="testuser", hashed_password="hashedpassword"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"


def test_clinic_model_creation(db_session):
    """Prueba la creación de modelo de clínica."""
    clinic = Clinic(
        name="Test Clinic",
        address="123 Test St",
        city="Test City",
        state="Test State",
        country="Test Country",
        postal_code="12345",
    )

    db_session.add(clinic)
    db_session.commit()
    db_session.refresh(clinic)

    assert clinic.id is not None
    assert clinic.name == "Test Clinic"
    assert clinic.address == "123 Test St"
