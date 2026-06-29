"""Conexión a la base de datos PostgreSQL con SQLAlchemy 2.0."""
from typing import Generator
from sqlalchemy.orm import Session
from app.infrastructure.database.session import engine, SessionLocal

def get_db() -> Generator[Session, None, None]:
    """Generador de sesión para dependencias."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Este archivo puede usarse también para inyección directa si se desea
DB_ENGINE = engine