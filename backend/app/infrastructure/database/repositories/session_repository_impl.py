"""Implementacion del repositorio de sesiones."""

from datetime import datetime
from typing import Any, cast

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.domain.repositories.session_repository import SessionRepository


class SessionDatabaseRepository(SessionRepository):
    """Repositorio de sesiones basado en SQLAlchemy.

    Esta implementacion mapea entre DTOs (dict) y modelos ORM.
    La interfaz de dominio no conoce los modelos ORM.
    """

    def __init__(self, db: DBSession) -> None:
        self.db = cast(DBSession, db)

    async def create_session(self, session_data: dict[str, Any]) -> dict[str, Any]:
        from app.infrastructure.database.models.session import Session as SessionModel

        model = SessionModel(**session_data)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return {k: getattr(model, k) for k in session_data.keys()}

    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> dict[str, Any] | None:
        from app.infrastructure.database.models.session import Session as SessionModel

        result = await self.db.execute(  # type: ignore[misc]
            select(SessionModel).where(
                SessionModel.refresh_token == refresh_token,
                SessionModel.is_active == True,  # noqa: E712
                SessionModel.revoked_at.is_(None),
            )
        )
        model = cast(SessionModel | None, result.scalar_one_or_none())
        return {k: getattr(model, k) for k in model.__dict__.keys()} if model else None

    async def revoke_session(self, session_id: int) -> bool:
        from app.infrastructure.database.models.session import Session as SessionModel

        result = await self.db.execute(  # type: ignore[misc]
            select(SessionModel).where(SessionModel.id == session_id)
        )
        model = cast(SessionModel | None, result.scalar_one_or_none())
        if model and model.is_active:  # type: ignore[assignment]
            model.is_active = False  # type: ignore[assignment]
            model.revoked_at = datetime.utcnow()  # type: ignore[assignment]
            await self.db.commit()  # type: ignore[misc,func-returns-value]
            return True
        return False

    async def revoke_all_user_sessions(self, user_id: int) -> int:
        from app.infrastructure.database.models.session import Session as SessionModel

        result = await self.db.execute(  # type: ignore[misc]
            select(SessionModel).where(
                SessionModel.user_id == user_id,
                SessionModel.is_active == True,  # noqa: E712
                SessionModel.revoked_at.is_(None),
            )
        )
        models = result.scalars().all()
        count = 0
        for model in models:
            model.is_active = False
            model.revoked_at = datetime.utcnow()
            count += 1
        if count > 0:
            await self.db.commit()  # type: ignore[misc,func-returns-value]
        return count
