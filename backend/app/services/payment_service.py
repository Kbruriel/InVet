"""Casos de uso de pagos operativos de servicios (BE-011-T04).

Centraliza las reglas de negocio de registro, cancelacion y calculo de
cambio. Los routers (BE-011-T05) mapean las excepciones de este modulo a
estados HTTP (402/404/409/422); este modulo NO conoce de HTTP.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.data.payment_repo import PaymentRepository
from app.domain.entities.appointment import Appointment
from app.domain.entities.payment import (
    Payment,
    PaymentCreate,
    PaymentMethod,
    PaymentStatus,
)
from app.domain.entities.service import Service
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.slice006_repositories import ServiceRepository


class PaymentError(Exception):
    """Error base de casos de uso de pagos."""

    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AppointmentNotFoundError(PaymentError):
    """La cita no existe o no pertenece al tenant (map a 404)."""

    def __init__(self, message: str = "La cita no existe o no es accesible.") -> None:
        super().__init__(message, status_code=404)


class ServiceNotFoundError(PaymentError):
    """El servicio no existe o no pertenece al tenant (map a 422)."""

    def __init__(
        self, message: str = "El servicio no existe o no es accesible."
    ) -> None:
        super().__init__(message, status_code=422)


class ServiceInactiveError(PaymentError):
    """El servicio no esta activo (map a 422)."""

    def __init__(
        self, message: str = "Solo se puede registrar un pago con un servicio activo."
    ) -> None:
        super().__init__(message, status_code=422)


class InvalidCashPaymentError(PaymentError):
    """Metodo CASH con importe recibido ausente o menor al cargo (map a 422)."""

    def __init__(
        self,
        message: str = "El importe recibido debe ser mayor o igual al importe del pago.",
    ) -> None:
        super().__init__(message, status_code=422)


class PaymentNotFoundError(PaymentError):
    """El pago no existe o no pertenece al tenant (map a 404)."""

    def __init__(self, message: str = "El pago no existe o no es accesible.") -> None:
        super().__init__(message, status_code=404)


class AlreadyCancelledError(PaymentError):
    """El pago ya fue cancelado (map a 409)."""

    def __init__(self, message: str = "El pago ya fue cancelado.") -> None:
        super().__init__(message, status_code=409)


def compute_change_amount(
    method: PaymentMethod,
    amount: int,
    amount_received: int | None,
) -> int | None:
    """Calcula el cambio: solo aplica cuando method=CASH y recibido >= cargo.

    En cualquier otro metodo (TRANSFER/CARD/OTHER) no se entrega cambio y
    el resultado es ``None``. Lanza ``InvalidCashPaymentError`` si el metodo
    es CASH y el importe recibido esta ausente o es menor al cargo.
    """
    if method != PaymentMethod.CASH:
        return None
    if amount_received is None:
        raise InvalidCashPaymentError()
    if amount_received < amount:
        raise InvalidCashPaymentError()
    return amount_received - amount


class CreatePaymentUseCase:
    """Registrar un pago operativo sobre una cita y un servicio activo.

    Reglas de negocio:
    - La cita debe existir en la misma clinica (``AppointmentNotFoundError`` -> 404).
    - El servicio debe existir en la misma clinica (``ServiceNotFoundError`` -> 422).
    - El servicio debe estar activo (``ServiceInactiveError`` -> 422).
    - El cambio solo se calcula cuando el metodo es CASH y
      ``amount_received >= amount`` (``InvalidCashPaymentError`` -> 422).
    - Estado inicial siempre ``PAID`` con ``paid_at`` poblado.
    """

    def __init__(
        self,
        payment_repository: PaymentRepository,
        appointment_repository: AppointmentRepository,
        service_repository: ServiceRepository,
    ) -> None:
        self.payment_repository = payment_repository
        self.appointment_repository = appointment_repository
        self.service_repository = service_repository

    async def execute(self, clinic_id: int, data: PaymentCreate) -> Payment:
        """Crear el pago validando cita, servicio y regla de cambio."""
        appointment: Appointment | None = await self.appointment_repository.get_by_id(
            data.appointment_id, clinic_id
        )
        if appointment is None:
            raise AppointmentNotFoundError()

        service: Service | None = await self.service_repository.get_service_by_id(
            data.service_id, clinic_id
        )
        if service is None:
            raise ServiceNotFoundError()
        if not service.is_active:
            raise ServiceInactiveError()

        change_amount = compute_change_amount(
            data.method, data.amount, data.amount_received
        )
        now = datetime.now(UTC)

        payment = Payment(
            id=None,
            appointment_id=data.appointment_id,
            service_id=data.service_id,
            clinic_id=clinic_id,
            amount=data.amount,
            method=data.method,
            amount_received=data.amount_received,
            change_amount=change_amount,
            status=PaymentStatus.PAID,
            paid_at=now,
            cancelled_at=None,
            created_by=data.created_by,
        )
        return await self.payment_repository.create(payment)


class CancelPaymentUseCase:
    """Cancelar un pago operativo ya registrado.

    Reglas de negocio:
    - El pago debe existir en la misma clinica (``PaymentNotFoundError`` -> 404).
    - Un pago ya ``CANCELLED`` no puede cancelarse de nuevo
      (``AlreadyCancelledError`` -> 409).
    """

    def __init__(self, payment_repository: PaymentRepository) -> None:
        self.payment_repository = payment_repository

    async def execute(self, payment_id: int, clinic_id: int) -> Payment:
        """Cancelar el pago por id con aislamiento por tenant."""
        payment = await self.payment_repository.get_by_id(payment_id, clinic_id)
        if payment is None:
            raise PaymentNotFoundError()
        if payment.status == PaymentStatus.CANCELLED:
            raise AlreadyCancelledError()
        cancelled = await self.payment_repository.cancel(payment_id, clinic_id)
        if cancelled is None:  # pragma: no cover (proteccion defensiva)
            raise PaymentNotFoundError()
        return cancelled


class PaymentService:
    """Fachada de casos de uso de pagos para el router (BE-011-T05).

    Agrupa ``CreatePaymentUseCase``/``CancelPaymentUseCase``/``list``/``get``
    para que el router no tenga que construir cada use case por separado.
    Todos los metodos reciben ``clinic_id`` (tenant) como primer argumento
    para forzar aislamiento por clinica.
    """

    def __init__(
        self,
        payment_repository: PaymentRepository,
        appointment_repository: AppointmentRepository,
        service_repository: ServiceRepository,
    ) -> None:
        self.payment_repository = payment_repository
        self.appointment_repository = appointment_repository
        self.service_repository = service_repository

    def create_payment(self) -> CreatePaymentUseCase:
        return CreatePaymentUseCase(
            self.payment_repository,
            self.appointment_repository,
            self.service_repository,
        )

    def cancel_payment(self) -> CancelPaymentUseCase:
        return CancelPaymentUseCase(self.payment_repository)

    async def get_payment(self, payment_id: int, clinic_id: int) -> Payment:
        """Obtener un pago por id con aislamiento por tenant (404 si no existe)."""
        payment = await self.payment_repository.get_by_id(payment_id, clinic_id)
        if payment is None:
            raise PaymentNotFoundError()
        return payment

    async def list_payments(
        self,
        clinic_id: int,
        appointment_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        status: PaymentStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        """Listar pagos del tenant con filtros opcionales y paginacion."""
        return await self.payment_repository.list(
            clinic_id=clinic_id,
            appointment_id=appointment_id,
            from_date=from_date,
            to_date=to_date,
            status=status,
            page=page,
            page_size=page_size,
        )
