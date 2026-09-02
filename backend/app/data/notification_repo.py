"""Repositorio de notificaciones internas (BE-013).

Interface ABC e implementacion SQLAlchemy para acceso a datos de la tabla
notifications con aislamiento por receptor y tenant.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.notification import Notification
from app.infrastructure.database.models.notification import (
    Notification as NotificationModel,
)


def _domain_from_model(model: NotificationModel) -> Notification:
    """Convierte un modelo ORM a entidad de dominio."""
    return Notification(
        id=model.id,
        clinic_id=model.clinic_id,
        user_id=model.user_id,
        event_type=model.event_type,
        subject=model.subject,
        body=model.body,
        ref_type=model.ref_type,
        ref_id=model.ref_id,
        is_read=model.is_read,
        read_at=model.read_at,
        created_at=model.created_at,
    )


class NotificationRepository(ABC):
    """Interface del repositorio de notificaciones."""

    @abstractmethod
    async def create_if_unique(
        self,
        clinic_id: int,
        user_id: int | None,
        event_type: str,
        subject: str,
        body: str,
        ref_type: str | None = None,
        ref_id: int | None = None,
    ) -> Notification | None:
        """Crear una notificacion solo si no existe la combinacion (user_id, event_type, ref_type, ref_id).

        Devuelve None si ya existe (dedup silencioso).
        """
        ...

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        clinic_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        """Listar notificaciones de un usuario filtradas por tenant y paginadas."""
        ...

    @abstractmethod
    async def get_by_id_for_user(
        self, notification_id: int, user_id: int
    ) -> Notification | None:
        """Obtener una notificacion verificando que pertenece al usuario receptor."""
        ...

    @abstractmethod
    async def mark_read(
        self, notification_id: int, user_id: int
    ) -> Notification | None:
        """Marcar una notificacion como leida si el usuario es el receptor."""
        ...

    @abstractmethod
    async def mark_all_read(self, user_id: int, clinic_id: int) -> int:
        """Marcar todas las no leidas de un usuario como leidas. Devuelve count actualizado."""
        ...

    @abstractmethod
    async def get_notification_for_user_key(
        self, user_id: int | None, event_type: str, ref_type: str, ref_id: int
    ) -> Notification | None:
        """Buscar existencia de una notificacion por clave de dedup (user_id, event_type, ref_type, ref_id)."""
        ...

    @abstractmethod
    async def count_unread(self, user_id: int, clinic_id: int) -> int:
        """Contar notificaciones no leidas de un usuario filtradas por tenant."""
        ...


class NotificationRepositoryImpl(NotificationRepository):
    """Implementacion SQLAlchemy del repositorio de notificaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def create_if_unique(
        self,
        clinic_id: int,
        user_id: int | None,
        event_type: str,
        subject: str,
        body: str,
        ref_type: str | None = None,
        ref_id: int | None = None,
    ) -> Notification | None:
        # Verificacion previa por clave de dedup para devolver None sin ejecutar
        # rollback sobre la transaccion del llamador: un integridad error aqui
        # abortaria el unit of work completo (p. ej. alta de cita + notificacion).
        existing = await self.get_notification_for_user_key(
            user_id, event_type, ref_type, ref_id
        )
        if existing is not None:
            return None
        model = NotificationModel(
            clinic_id=clinic_id,
            user_id=user_id,
            event_type=event_type,
            subject=subject[:2048],
            body=body[:2048],
            ref_type=ref_type,
            ref_id=ref_id,
        )
        self.db.add(model)
        try:
            self.db.flush()
            self.db.refresh(model)
            return _domain_from_model(model)
        except Exception:
            # Ultimo resguardo ante carrera de escritura: la unique constraint
            # uq_notifications_dedup impide la doble fila. Requiere rollback
            # porque la transaccion queda en estado de error.
            self.db.rollback()
            return None

    async def list_by_user(
        self,
        user_id: int,
        clinic_id: int,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        """Listar notificaciones paginadas por receptor y tenant."""
        base_stmt = (
            select(NotificationModel)
            .where(NotificationModel.clinic_id == clinic_id)
            .where(NotificationModel.user_id == user_id)
        )

        if unread_only:
            base_stmt = base_stmt.where(
                NotificationModel.is_read == False
            )  # noqa: E712

        total_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(total_stmt).scalar() or 0

        base_stmt = base_stmt.order_by(NotificationModel.created_at.desc())

        offset = (page - 1) * page_size
        paginated_stmt = base_stmt.offset(offset).limit(page_size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total

    async def get_by_id_for_user(
        self, notification_id: int, user_id: int
    ) -> Notification | None:
        """Obtener notificacion por ID y usuario (tenant isolation implicito via user_id)."""
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .where(NotificationModel.user_id == user_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return _domain_from_model(result)

    async def mark_read(
        self, notification_id: int, user_id: int
    ) -> Notification | None:
        """Marcar una notificacion como leida si el usuario es el receptor."""
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .where(NotificationModel.user_id == user_id)
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        model.is_read = True
        model.read_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def mark_all_read(self, user_id: int, clinic_id: int) -> int:
        """Marcar todas las no leidas de un usuario como leidas. Retorna count actualizado."""
        stmt = select(NotificationModel).where(
            NotificationModel.user_id == user_id,
            NotificationModel.clinic_id == clinic_id,
            NotificationModel.is_read == False,  # noqa: E712
        )
        models = self.db.execute(stmt).scalars().all()
        count = len(models)
        for m in models:
            m.is_read = True
            m.read_at = datetime.now(UTC)
        if count > 0:
            self.db.flush()
        return count

    async def count_unread(self, user_id: int, clinic_id: int) -> int:
        """Contar notificaciones no leidas de un usuario filtradas por tenant."""
        stmt = select(func.count()).select_from(
            select(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.clinic_id == clinic_id,
                NotificationModel.is_read == False,  # noqa: E712
            )
            .subquery()
        )
        return self.db.execute(stmt).scalar() or 0

    async def get_notification_for_user_key(
        self, user_id: int | None, event_type: str, ref_type: str, ref_id: int
    ) -> Notification | None:
        """Buscar existencia de una notificacion por clave de dedup (user_id, event_type, ref_type, ref_id)."""
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .where(NotificationModel.event_type == event_type)
            .where(NotificationModel.ref_type == ref_type)
            .where(NotificationModel.ref_id == ref_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()


def get_notification_repo(db: Session) -> NotificationRepository:
    """Obtener una instancia concreta del repositorio de notificaciones."""
    return NotificationRepositoryImpl(db)
