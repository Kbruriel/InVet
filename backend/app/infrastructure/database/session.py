"""Manejo de sesiones de base de datos."""
import os
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

def _create_engine():
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

# Base para modelos ORM
Base = declarative_base()


def get_db() -> Session:
    """Obtiene una sesión de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
