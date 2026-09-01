"""Modelo ORM para notificaciones internas (BE-013)."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import text as sa_text

from app.infrastructure.database.models.base import Base


class Notification(Base):
    """Notificacion interna de una clinica."""

    __tablename__ = "notifications"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_type",
            "ref_type",
            "ref_id",
            name="uq_notifications_dedup",
        ),
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_is_read", "is_read"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    clinic_id = Column(
        Integer,
        ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Receptor del mensaje: usuario autenticado (tabla users), no interna.
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type = Column(String(50), nullable=False)
    subject = Column(String(2048), nullable=False)
    body = Column(Text, nullable=False)
    ref_type = Column(String(50), nullable=True)
    ref_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, server_default=sa_text("false"), nullable=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(
        DateTime, server_default=sa_text("CURRENT_TIMESTAMP"), nullable=False
    )
