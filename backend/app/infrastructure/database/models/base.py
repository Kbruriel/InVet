"""Modelo base para las entidades de la base de datos."""

from typing import Any

from sqlalchemy.ext.hybrid import hybrid_property

from app.infrastructure.database.session import Base

__all__ = ["Base", "BaseModel"]


class BaseModel:
    """Clase base para entidades."""

    @hybrid_property
    def dict(self) -> dict[str, Any]:
        """Convierte el modelo a diccionario."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"
