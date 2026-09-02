"""Modelos ORM para soporte básico (BE-014 y soporte técnico).

Sin server_default en columnas DateTime ni status para evitar parseo de
literral 'CURRENT_TIMESTAMP'/'iniciado' que SQLA fall al interpretar como
datetime/bool con SQLite + RETURNING. Los valores default se setean
explícitamente en el repo layer al insertar entidades ORM.
"""

from __future__ import annotations

import enum

import sqlalchemy as sa
from sqlalchemy import (
    Column,
    DateTime,
    Index,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base

# ------------------------------------------------------------------ #
# Enum de estados
# ------------------------------------------------------------------ #


class TicketStatus(str, enum.Enum):
    """Estados posibles de un ticket de soporte."""

    INICIADO = "iniciado"
    PENDIENTE = "pendiente"
    PROCESO = "proceso"
    COMPLETADO = "completado"
    CERRADO = "cerrado"


# ------------------------------------------------------------------ #
# Tabla ticket_category  (AC-014-06, AC-014-02)
# Sin active default ni server_default para evitar problemas.
# El seed de test setea active=True explicitamente.
# Sin server_default en created_at -> el fixture lo setea en la entidad.
# ------------------------------------------------------------------ #


class TicketCategory(Base):
    """Categorías de tickets asociadas a una clinica."""

    __tablename__ = "ticket_categories"

    id = Column("id", sa.Integer(), primary_key=True, autoincrement=True)
    clinic_id = Column(
        "clinic_id",
        sa.Integer(),
        sa.ForeignKey("clinics.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(sa.String(100), nullable=False)
    description = Column(sa.Text(), nullable=True)
    active = Column(sa.Boolean(), default=False, nullable=False)
    created_at = Column(DateTime, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("clinic_id", "name", name="uq_ticket_category_clinic"),
    )

    tickets = relationship("SupportTicket", lazy="select")


# ------------------------------------------------------------------ #
# Tabla support_ticket  (AC-014-01, AC-014-02)
# Sin server_default en status/created_at/updated_at.
# El repo setea todos estos campos explicitamente al crear.
# ------------------------------------------------------------------ #


class SupportTicket(Base):
    """Ticket de soporte para solicitudes del cliente."""

    __tablename__ = "support_tickets"

    id = Column(sa.Integer(), primary_key=True, autoincrement=True)
    title = Column(sa.String(200), nullable=False)
    description = Column(sa.Text(), nullable=True)
    status = Column(sa.String(20), nullable=False)
    category_id = Column(
        sa.Integer(), sa.ForeignKey("ticket_categories.id"), nullable=True
    )
    owner_id = Column(
        sa.Integer(), sa.ForeignKey("owners.id", ondelete="CASCADE"), nullable=False
    )
    clinic_id = Column(
        sa.Integer(), sa.ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_support_tickets_owner_id", "owner_id"),
        Index("ix_support_tickets_clinic_id", "clinic_id"),
        Index("ix_support_tickets_status", "status"),
    )

    category = relationship("TicketCategory", lazy="select")
    owner = relationship("Owner", lazy="noload")


# ------------------------------------------------------------------ #
# Exports
# ------------------------------------------------------------------ #

__all__: tuple[str, ...] = ("SupportTicket", "TicketCategory", "TicketStatus")
