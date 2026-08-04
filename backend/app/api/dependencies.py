"""Dependencias compartidas para routers API."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.auth_use_case import AuthUseCase
from app.infrastructure.database import get_db
from app.infrastructure.database.repositories.user_repository_impl import (
    UserDatabaseRepository,
)


def get_auth_use_case(db: Session = Depends(get_db)) -> AuthUseCase:
    """Construye el caso de uso de autenticacion."""
    return AuthUseCase(UserDatabaseRepository(db))
