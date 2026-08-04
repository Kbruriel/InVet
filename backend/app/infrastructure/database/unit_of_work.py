"""Manejo de Unit of Work para transacciones."""

from collections.abc import Generator
from types import TracebackType

from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal


class UnitOfWork:
    """Unit of Work para manejar transacciones."""

    def __init__(self) -> None:
        self.session: Session = SessionLocal()

    def __enter__(self) -> Session:
        return self.session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            # Si hay una excepción, hacer rollback
            self.session.rollback()
        else:
            # Si no hay excepción, hacer commit
            self.session.commit()
        self.session.close()

    def commit(self) -> None:
        """Confirma las transacciones."""
        self.session.commit()

    def rollback(self) -> None:
        """Revierte las transacciones."""
        self.session.rollback()

    def close(self) -> None:
        """Cierra la sesión."""
        self.session.close()


def get_uow() -> Generator[UnitOfWork, None, None]:
    """Obtiene una instancia de UnitOfWork para inyección de dependencias."""
    uow = UnitOfWork()
    try:
        yield uow
    finally:
        uow.close()
