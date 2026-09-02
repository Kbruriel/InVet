"""Router FastAPI para pagos operativos de servicios (BE-011-T05).

Expone los endpoints CRUD de pagos sin logica de negocio: los casos de uso de
``app.services.payment_service`` encapsulan las reglas, y el router solo mapea
las excepciones de dominio a estados HTTP (401/403/404/409/422).
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.payment_schemas import PaymentCreate, PaymentPage, PaymentRead
from app.core.security import get_current_access_user
from app.data.payment_repo import PaymentRepository
from app.domain.entities.payment import PaymentStatus
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.slice006_repositories import (
    InternalUserRepository,
    ServiceRepository,
)
from app.infrastructure.database.repositories.appointment_repository_impl import (
    AppointmentRepositoryImpl,
)
from app.infrastructure.database.repositories.factory import (
    get_internal_user_repo as _factory_internal_user,
)
from app.infrastructure.database.repositories.service_repository_impl import (
    ServiceRepositoryImpl,
)
from app.services.payment_service import PaymentError, PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])

# Roles que pueden crear/cancelar un pago operativo (rol clinico).
_WRITE_ROLES = {"veterinarian", "clinic", "staff", "admin"}


# ---------------------------------------------------------------------------
# Dependencias (sobreescrituras de FastAPI, sobreescribibles en tests)
# ---------------------------------------------------------------------------
def get_current_db() -> Generator[Session, None, None]:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    yield from _get_db()


def get_payment_repo(db: Session = Depends(get_current_db)) -> PaymentRepository:
    """Repositorio de pagos (ABC + impl. SQLAlchemy)."""
    from app.data.payment_repo import PaymentRepositoryImpl

    return PaymentRepositoryImpl(db)


def get_appointment_repo(
    db: Session = Depends(get_current_db),
) -> AppointmentRepository:
    """Repositorio de citas (para validacion en el use case de creacion)."""
    return AppointmentRepositoryImpl(db)


def get_service_repo(db: Session = Depends(get_current_db)) -> ServiceRepository:
    """Repositorio de servicios (para validacion en el use case de creacion)."""
    return ServiceRepositoryImpl(db)


def get_internal_user_repo(
    db: Session = Depends(get_current_db),
) -> InternalUserRepository:
    """Usuario interno (resolución de ``created_by``)."""
    return _factory_internal_user(db)


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payment_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    service_repo: ServiceRepository = Depends(get_service_repo),
) -> PaymentService:
    """Fachada de casos de uso de pagos (BE-011-T04)."""
    return PaymentService(payment_repo, appointment_repo, service_repo)


# ---------------------------------------------------------------------------
# Helpers de tenant / rol
# ---------------------------------------------------------------------------
def _extract_user_id(current_user: dict) -> int:
    user_id = current_user.get("user_id") or current_user.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado.",
        )
    return int(user_id)


def _get_clinic_id_from_user(current_user: dict) -> int:
    clinic_id = current_user.get("clinic_id") or current_user.get("tenant_id")
    if clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una clínica asociada.",
        )
    return int(clinic_id)


def _require_write_role(current_user: dict) -> None:
    role = current_user.get("role")
    if role not in _WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un veterinario o staff de clínica puede registrar/cancelar pagos.",
        )


async def _resolve_created_by(
    internal_user_repo: InternalUserRepository, user_id: int, clinic_id: int
) -> int | None:
    """``payments.created_by`` referencia ``internal_users.id`` (no ``users.id``)."""
    internal_user = await internal_user_repo.get_by_user_id(user_id, clinic_id)
    return internal_user.id if internal_user else None


# ---------------------------------------------------------------------------
# POST /payments — registrar pago operativo
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar pago operativo de un servicio",
)
async def create_payment(
    payload: PaymentCreate,
    current_user: dict = Depends(get_current_access_user),
    service: PaymentService = Depends(get_payment_service),
    internal_user_repo: InternalUserRepository = Depends(get_internal_user_repo),
    db: Session = Depends(get_current_db),
) -> PaymentRead:
    """Registrar un pago operativo sobre una cita y un servicio activos.

    - Solo roles clínicos (veterinarian/staff/admin) pueden crear (403).
    - La cita debe existir en la clínica del usuario (404).
    - El servicio debe existir y estar activo (422).
    - Cambio solo cuando ``method=CASH`` y ``amount_received >= amount`` (422).
    """
    _require_write_role(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)
    user_id = _extract_user_id(current_user)
    created_by = await _resolve_created_by(internal_user_repo, user_id, clinic_id)

    domain_data = payload.model_copy(update={"created_by": created_by})
    use_case = service.create_payment()

    try:
        result = await use_case.execute(clinic_id=clinic_id, data=domain_data)
    except (
        PaymentError
    ) as exc:  # AppointmentNotFoundError / ServiceNotFoundError / ServiceInactiveError / InvalidCashPaymentError
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None

    # BE-013-T06: emit notificacion al owner del pet asociado a la cita pagada
    from app.api.v1.routers._notify import emit_notify

    event_type = None
    if result and result.status:
        status_val = (
            result.status.value
            if hasattr(result.status, "value")
            else str(result.status)
        )
        if status_val == "paid":
            event_type = "payment_completed"
        elif status_val == "cancelled":
            event_type = "payment_cancelled"
    appointment_id = getattr(result, "appointment_id", None) if result else None
    if event_type and appointment_id:
        try:
            from app.infrastructure.database.models.appointment import (
                Appointment as AppointmentModel,
            )
            from app.infrastructure.database.models.owner import Owner

            appt = (
                db.query(AppointmentModel)
                .filter(AppointmentModel.id == appointment_id)
                .first()
            )
            pet_obj = getattr(appt, "pet", None) if appt else None
            pet_display = str(appt.pet_id) if appt else "servicio"
            owner_user_id = None
            owner_email = None
            if pet_obj:
                owner = db.query(Owner).filter(Owner.id == pet_obj.owner_id).first()
                if owner:
                    owner_user_id = int(owner.user_id)
                    owner_email = owner.email
            if owner_user_id:
                await emit_notify(
                    db=db,
                    recipient_user_id=owner_user_id,
                    recipient_email=owner_email,
                    clinic_id=clinic_id,
                    event_type=event_type,
                    ref_entity="payment",
                    ref_id=result.id,
                    body_extra=f"Pago procesado: {status_val} | Monto: {result.amount if hasattr(result, 'amount') else ''}",
                )
        except Exception:
            # BE-013: un fallo de notificacion no debe romper la creacion del pago.
            pass

    return PaymentRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /payments/{payment_id} — obtener detalle
# ---------------------------------------------------------------------------
@router.get(
    "/{payment_id}",
    response_model=PaymentRead,
    summary="Obtener detalle de un pago operativo",
)
async def get_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_access_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentRead:
    """Obtener detalle de un pago.

    - Solo usuarios con clínica asociada pueden ver (403 si no hay tenant).
    - Pagos de otra clínica se consideran no existentes (404, consistente con
      la creacion).
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    try:
        result = await service.get_payment(payment_id, clinic_id)
    except PaymentError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
    return PaymentRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /payments — listado paginado con filtros
# ---------------------------------------------------------------------------
@router.get(
    "",
    response_model=PaymentPage,
    summary="Listar pagos operativos de la clínica",
)
async def list_payments(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    appointment_id: int | None = Query(
        None, gt=0, description="Filtrar por cita (opcional)"
    ),
    from_date: datetime | None = Query(
        None, description="Fecha/hora inicio del rango (opcional)"
    ),
    to_date: datetime | None = Query(
        None, description="Fecha/hora fin del rango (opcional)"
    ),
    status_filter: PaymentStatus | None = Query(
        None, alias="status", description="Filtrar por estado (paid/cancelled)"
    ),
    current_user: dict = Depends(get_current_access_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentPage:
    """Listado paginado de pagos de la clínica del usuario (tenant isolation).

    Soporta filtros opcionales por periodo, cita y estado. Meta con
    ``page``, ``page_size``, ``total``, ``pages``.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    items, total = await service.list_payments(
        clinic_id=clinic_id,
        appointment_id=appointment_id,
        from_date=from_date,
        to_date=to_date,
        status=status_filter,
        page=page,
        page_size=page_size,
    )
    return PaymentPage(
        items=[PaymentRead.model_validate(i) for i in items],
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    )


# ---------------------------------------------------------------------------
# POST /payments/{payment_id}/cancel — cancelar pago
# ---------------------------------------------------------------------------
@router.post(
    "/{payment_id}/cancel",
    response_model=PaymentRead,
    summary="Cancelar un pago operativo",
)
async def cancel_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_access_user),
    service: PaymentService = Depends(get_payment_service),
) -> PaymentRead:
    """Cancelar un pago operativo.

    - Solo roles clínicos (veterinarian/staff/admin) pueden cancelar (403).
    - El pago debe existir en la clínica del usuario (404).
    - Cancelar un pago ya CANCELLED devuelve 409.
    """
    _require_write_role(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)
    use_case = service.cancel_payment()
    try:
        result = await use_case.execute(payment_id=payment_id, clinic_id=clinic_id)
    except PaymentError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from None
    return PaymentRead.model_validate(result)
