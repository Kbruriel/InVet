"""Manejo de sesiones de base de datos."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.infrastructure.database.models.base import Base

__all__ = ["Base", "SessionLocal", "engine", "get_db"]


def _create_engine() -> Engine:
    """Crea el motor principal y cae a SQLite en entornos sin driver PostgreSQL."""
    try:
        return create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,  # Cambiar a True para debugging
        )
    except ModuleNotFoundError as exc:
        if "psycopg2" not in str(exc):
            raise

        if os.getenv("INVET_ALLOW_SQLITE_FALLBACK") != "1":
            raise RuntimeError(
                "PostgreSQL driver psycopg2 no esta disponible. "
                "Configura una base de datos compatible o habilita "
                "INVET_ALLOW_SQLITE_FALLBACK=1 para pruebas locales."
            ) from exc

        # Permite importar el backend en entornos de prueba sin psycopg2.
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )


# Crear motor de base de datos
engine = _create_engine()

# Crear la clase de sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Obtiene una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
