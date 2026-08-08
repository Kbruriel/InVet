"""Implementacion del repositorio de sesiones."""

from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.domain.repositories.session_repository import SessionRepository
from app.infrastructure.database.models.session import Session as SessionModel


class SessionDatabaseRepository(SessionRepository):
    """Repositorio de sesiones basado en SQLAlchemy."""

    def __init__(self, db: DBSession) -> None:
        self.db = cast(DBSession, db)

    async def create_session(self, session: SessionModel) -> SessionModel:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return cast(SessionModel, session)

    async def get_session_by_refresh_token(
        self, refresh_token: str
    ) -> SessionModel | None:
        result = await self.db.execute(  # type: ignore[misc]
            select(SessionModel).where(
                SessionModel.refresh_token == refresh_token,
                SessionModel.is_active == True,  # noqa: E712
                SessionModel.revoked_at.is_(None),
            )
        )
        return cast(SessionModel | None, result.scalar_one_or_none())

    async def revoke_session(self, session_id: int) -> bool:
        result = await self.db.execute(  # type: ignore[misc]
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session = cast(SessionModel | None, result.scalar_one_or_none())
        if session and session.is_active:
            session.is_active = False  # type: ignore[assignment]
            session.revoked_at = datetime.utcnow()  # type: ignore[assignment]
            await self.db.commit()  # type: ignore[misc,func-returns-value]
            return True
        return False

    async def revoke_all_user_sessions(self, user_id: int) -> int:
        result = await self.db.execute(  # type: ignore[misc]
            select(SessionModel).where(
                SessionModel.user_id == user_id,
                SessionModel.is_active == True,  # noqa: E712
                SessionModel.revoked_at.is_(None),
            )
        )
        sessions = result.scalars().all()
        count = 0
        for session in sessions:
            session.is_active = False
            session.revoked_at = datetime.utcnow()
            count += 1
        if count > 0:
            await self.db.commit()  # type: ignore[misc,func-returns-value]
        return count
