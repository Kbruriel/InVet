"""Compatibilidad para tests y scripts que importan `app.main`."""

from app.api.main import app, create_app

__all__ = ["app", "create_app"]
