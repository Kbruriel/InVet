"""Compatibilidad para imports históricos de conexión a BD."""

from app.infrastructure.database.session import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
