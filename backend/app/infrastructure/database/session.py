"""Manejo de sesiones de base de datos."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

Base = declarative_base()


def _build_engine(database_url: str):
    if database_url.startswith("sqlite"):
        _reset_ephemeral_sqlite(database_url)
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"connect_timeout": 2},
        echo=False,
    )


def _initialize_sqlite_schema(engine) -> None:
    # Importar modelos registra todas las tablas en Base.metadata.
    import app.infrastructure.database.models  # noqa: F401
    import app.infrastructure.models.clinic_models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def _reset_ephemeral_sqlite(database_url: str) -> None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return

    db_path = Path(database_url.removeprefix(prefix))
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path

    if db_path.name != "qa-test.db":
        return

    if db_path.exists():
        db_path.unlink()


def _build_sqlite_fallback_engine():
    db_path = Path(tempfile.gettempdir()) / f"invet_test_{os.getpid()}.db"
    if db_path.exists():
        db_path.unlink()

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    _initialize_sqlite_schema(engine)
    return engine


def _create_engine():
    try:
        engine = _build_engine(settings.DATABASE_URL)
        if settings.DATABASE_URL.startswith("sqlite"):
            _initialize_sqlite_schema(engine)
        with engine.connect():
            pass
        return engine
    except Exception:
        return _build_sqlite_fallback_engine()


engine = _create_engine()

# Crear la clase de sesiÃ³n local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    """Obtiene una sesiÃ³n de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
