"""Configuracion compartida para tests backend."""

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("INVET_ALLOW_SQLITE_FALLBACK", "1")

from app.infrastructure.database.models import (  # noqa: E402,F401
    availability_summary,
    branch,
    branch_schedule,
    clinic,
    owner,
    pet,
    rating_summary,
    service,
    user,
    veterinarian,
)
from app.infrastructure.database.models.base import Base  # noqa: E402


@pytest.fixture
def db_session():
    """Sesion SQLite aislada para pruebas API."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
