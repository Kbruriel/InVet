"""Modelo base para las entidades de la base de datos."""

from typing import Any, cast

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base

# Usar Base declarative como clase base para los modelos ORM
Base = declarative_base()


class BaseModel:
    """Clase base para entidades."""

    @hybrid_property
    def dict(self) -> dict[str, Any]:
        """Convierte el modelo a diccionario."""
        table = cast(Any, self).__table__
        return {c.name: getattr(self, c.name) for c in table.columns}

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_")
        )
        return f"{self.__class__.__name__}({attrs})"
