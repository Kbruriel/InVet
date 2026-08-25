"""Modelo ORM de pagos operativos de servicios para BE-011."""

from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    text,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class _PaymentMethod(PyEnum):
    """Valores crudos para el enum de metodos de pago (solo uso interno de ORM)."""

    CASH = "cash"
    TRANSFER = "transfer"
    CARD = "card"
    OTHER = "other"


class _PaymentStatus(PyEnum):
    """Valores crudos para el enum de estados de pago (solo uso interno de ORM)."""

    PAID = "paid"
    CANCELLED = "cancelled"


class Payment(Base):
    """Modelo de pagos operativos de servicios para la base de datos (BE-011)."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(
        Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False
    )
    service_id = Column(
        Integer, ForeignKey("services.id", ondelete="RESTRICT"), nullable=False
    )
    clinic_id = Column(
        Integer, ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Integer, nullable=False)  # Stored in cents (integer)
    method = Column(
        Enum(
            _PaymentMethod,
            name="payment_method_enum",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=_PaymentMethod.CASH,
    )
    amount_received = Column(Integer, nullable=True)  # Stored in cents (integer)
    change_amount = Column(Integer, nullable=True)  # Stored in cents (integer)
    status = Column(
        Enum(
            _PaymentStatus,
            name="payment_status_enum",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=_PaymentStatus.PAID,
    )
    paid_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
    )
    cancelled_at = Column(DateTime, nullable=True)
    created_by = Column(
        Integer, ForeignKey("internal_users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relaciones
    appointment = relationship("Appointment", lazy="noload")
    service = relationship("Service", lazy="noload")
    clinic = relationship("Clinic", lazy="noload")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, appointment_id={self.appointment_id}, status={self.status.name})>"
