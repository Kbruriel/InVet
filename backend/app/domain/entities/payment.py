"""Entidades de dominio para pagos operativos de servicios (BE-011)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentMethod(str, Enum):
    """Metodos de pago operativo."""

    CASH = "cash"
    TRANSFER = "transfer"
    CARD = "card"
    OTHER = "other"


class PaymentStatus(str, Enum):
    """Estados de un pago operativo."""

    PAID = "paid"
    CANCELLED = "cancelled"


class Payment(BaseModel):
    """Pago operativo de servicio (salida completa)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    appointment_id: int = Field(..., gt=0)
    service_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    amount: int = Field(..., ge=0)
    method: PaymentMethod
    amount_received: int | None = Field(None, ge=0)
    change_amount: int | None = Field(None, ge=0)
    status: PaymentStatus
    paid_at: datetime
    cancelled_at: datetime | None = None
    created_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PaymentCreate(BaseModel):
    """Datos de entrada para registrar un pago (caso de uso)."""

    appointment_id: int = Field(..., gt=0)
    service_id: int = Field(..., gt=0)
    amount: int = Field(..., ge=0)
    method: PaymentMethod
    amount_received: int | None = Field(None, ge=0)
    created_by: int | None = None
