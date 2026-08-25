"""Repositorio de pagos operativos de servicios para BE-011.

Este modulo concentra la interface (ABC) y la implementacion SQLAlchemy para
mantener el acceso a datos tipado y testeable sin logica de negocio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.infrastructure.database.models.payment import Payment as PaymentModel


def _domain_from_model(model: PaymentModel) -> Payment:
    """Convierte un modelo ORM a entidad de dominio."""
    def _v(val: object) -> str:
        return getattr(val, "value", val)

    return Payment(
        id=model.id,
        appointment_id=model.appointment_id,
        service_id=model.service_id,
        clinic_id=model.clinic_id,
        amount=model.amount,
        method=PaymentMethod(_v(model.method)),
        amount_received=model.amount_received,
        change_amount=model.change_amount,
        status=PaymentStatus(_v(model.status)),
        paid_at=model.paid_at,
        cancelled_at=model.cancelled_at,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class PaymentRepository(ABC):
    """Interface para el repositorio de pagos operativos."""

    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        """Crear y persistir un pago."""
        pass

    @abstractmethod
    async def get_by_id(
        self, payment_id: int, clinic_id: int
    ) -> Payment | None:
        """Obtener pago por ID con aislamiento de tenant (clinic_id)."""
        pass

    @abstractmethod
    async def list(
        self,
        clinic_id: int,
        appointment_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        status: PaymentStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        """Listar pagos por tenant con filtros opcionales y paginacion."""
        pass

    @abstractmethod
    async def cancel(self, payment_id: int, clinic_id: int) -> Payment | None:
        """Cancelar un pago (estado CANCELLED + cancelled_at)."""
        pass


class PaymentRepositoryImpl(PaymentRepository):
    """Implementacion SQLAlchemy del repositorio de pagos operativos."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def create(self, payment: Payment) -> Payment:
        """Crear y persistir un pago."""
        model = PaymentModel(
            appointment_id=payment.appointment_id,
            service_id=payment.service_id,
            clinic_id=payment.clinic_id,
            amount=payment.amount,
            method=payment.method.value,
            amount_received=payment.amount_received,
            change_amount=payment.change_amount,
            status=payment.status.value,
            paid_at=payment.paid_at,
            cancelled_at=payment.cancelled_at,
            created_by=payment.created_by,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def get_by_id(
        self, payment_id: int, clinic_id: int
    ) -> Payment | None:
        """Obtener pago por ID y clinic_id (tenant isolation)."""
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .where(PaymentModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return _domain_from_model(result)

    async def list(
        self,
        clinic_id: int,
        appointment_id: int | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        status: PaymentStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        """Listar pagos por tenant con filtros opcionales y paginacion."""
        base_stmt = select(PaymentModel).where(
            PaymentModel.clinic_id == clinic_id
        )
        if appointment_id is not None:
            base_stmt = base_stmt.where(
                PaymentModel.appointment_id == appointment_id
            )
        if from_date is not None:
            base_stmt = base_stmt.where(PaymentModel.paid_at >= from_date)
        if to_date is not None:
            base_stmt = base_stmt.where(PaymentModel.paid_at <= to_date)
        if status is not None:
            base_stmt = base_stmt.where(PaymentModel.status == status.value)
        base_stmt = base_stmt.order_by(PaymentModel.id.desc())

        count_stmt = select(func.count()).select_from(
            base_stmt.subquery()
        )
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * page_size
        paginated_stmt = base_stmt.offset(offset).limit(page_size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total

    async def cancel(self, payment_id: int, clinic_id: int) -> Payment | None:
        """Cancelar un pago por id y clinic_id (tenant isolation)."""
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.id == payment_id)
            .where(PaymentModel.clinic_id == clinic_id)
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        model.status = PaymentStatus.CANCELLED.value
        model.cancelled_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)


def get_payment_repo(db: Session) -> PaymentRepository:
    """Obtener una instancia concreta del repositorio de pagos."""
    return PaymentRepositoryImpl(db)
