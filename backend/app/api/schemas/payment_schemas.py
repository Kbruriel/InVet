"""Schemas Pydantic para pagos operativos de servicios (BE-011)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.payment import PaymentMethod


class PaymentCreate(BaseModel):
    """Schema para registrar un pago operativo desde el frontend.

    - ``appointment_id`` debe referir a una cita de la clinica del usuario.
    - ``service_id`` debe referir a un servicio activo de la clinica del usuario.
    - ``amount_received`` es obligatorio y >= ``amount`` cuando ``method=CASH``.
    - ``clinic_id`` se resuelve del usuario autenticado (tenant isolation).
    """

    appointment_id: int = Field(..., gt=0, description="ID de la cita asociada")
    service_id: int = Field(..., gt=0, description="ID del servicio cobrado")
    amount: int = Field(
        ...,
        ge=0,
        description="Importe del pago (menor unidad de moneda, ej. centavos de peso)",
    )
    method: PaymentMethod = Field(
        ...,
        description="Metodo de pago (cash, transfer, card, other)",
    )
    amount_received: int | None = Field(
        None,
        ge=0,
        description="Importe recibido. Obligatorio y >= amount cuando method=cash.",
    )


class PaymentRead(BaseModel):
    """Schema de respuesta para un pago operativo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    service_id: int
    clinic_id: int
    amount: int
    method: PaymentMethod
    amount_received: int | None = None
    change_amount: int | None = None
    status: str
    paid_at: datetime
    cancelled_at: datetime | None = None
    created_by: int | None = None


class PaymentPage(BaseModel):
    """Respuesta paginada de pagos operativos."""

    items: list[PaymentRead]
    meta: dict
