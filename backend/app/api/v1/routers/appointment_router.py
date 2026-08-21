"""Router FastAPI para citas médicas (BE-008)."""

from collections.abc import Generator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.appointment_schemas import (
    AppointmentCreateSchema,
    AppointmentListSchema,
    AppointmentReadSchema,
    AppointmentUpdateSchema,
    AvailabilityResponseSchema,
    AvailabilitySlotSchema,
    StatusTransitionSchema,
)
from app.application.appointment_use_cases import (
    CreateAppointmentUseCase,
    GetAppointmentUseCase,
    GetAvailabilityUseCase,
    ListAppointmentsByClinicUseCase,
    ListAppointmentsByOwnerUseCase,
    TransitionAppointmentStatusUseCase,
    UpdateAppointmentUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.appointment_repository import AppointmentRepository


def get_current_db() -> Generator[Session, None, None]:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    yield from _get_db()


router = APIRouter(prefix="/appointments", tags=["appointments"])


def get_appointment_repo(
    db: Session = Depends(get_current_db),
) -> AppointmentRepository:
    """Dependencia para el repositorio de citas."""
    from app.infrastructure.database.repositories.factory import (
        get_appointment_repo as _get,
    )

    return _get(db)


def _extract_user_id(current_user: dict) -> int:
    """Extraer user_id del usuario autenticado."""
    user_id = current_user.get("user_id") or current_user.get("id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo identificar al usuario autenticado.",
        )
    return int(user_id)


def _get_clinic_id_from_user(current_user: dict) -> int:
    """Extraer clinic_id del usuario para tenant isolation."""
    clinic_id = current_user.get("clinic_id") or current_user.get("tenant_id")
    if clinic_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene una clínica asociada.",
        )
    return int(clinic_id)


# ---------------------------------------------------------------------------
# GET /appointments/availability
# IMPORTANTE: debe declararse ANTES que GET /{appointment_id} para que
# "availability" no sea capturado como parámetro dinámico.
# ---------------------------------------------------------------------------
@router.get(
    "/availability",
    response_model=AvailabilityResponseSchema,
    summary="Obtener disponibilidad de horarios",
)
async def get_appointment_availability(
    date: str = Query(..., description="Fecha a consultar (YYYY-MM-DD)"),
    veterinarian_id: int
    | None = Query(None, description="ID del veterinario (opcional)"),
    clinic_id: int | None = Query(None, description="ID de la clínica"),
    branch_id: int | None = Query(None, description="ID de la sucursal (opcional)"),
    slot_duration: int = Query(
        30, ge=15, le=120, description="Duración del slot en minutos"
    ),
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AvailabilityResponseSchema:
    """Obtener slots disponibles para agendar citas.

    Query params:
    - date: Fecha obligatoria
    - veterinarian_id: Filtrar por veterinario específico (opcional)
    - clinic_id: ID de la clínica (obligatorio si no está en el token)
    - branch_id: Filtrar por sucursal (opcional)
    - slot_duration: Duración del slot en minutos (15-120)
    """
    if clinic_id is None:
        clinic_id = _get_clinic_id_from_user(current_user)

    try:
        query_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La fecha debe estar en formato YYYY-MM-DD",
        ) from exc

    use_case = GetAvailabilityUseCase(repo)
    slots = await use_case.execute(
        veterinarian_id=veterinarian_id,
        clinic_id=clinic_id,
        branch_id=branch_id,
        date=query_date,
        slot_duration_minutes=slot_duration,
    )

    return AvailabilityResponseSchema(
        date=date,
        slots=[AvailabilitySlotSchema(**s) for s in slots],
        meta={
            "veterinarian_id": veterinarian_id,
            "branch_id": branch_id,
            "slot_duration_minutes": slot_duration,
        },
    )


# ---------------------------------------------------------------------------
# GET /appointments/{appointment_id}
# ---------------------------------------------------------------------------
@router.get(
    "/{appointment_id}",
    response_model=AppointmentReadSchema,
    summary="Obtener cita por ID",
)
async def get_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentReadSchema:
    """Obtener una cita por ID con validación de tenant."""
    _clinic_id = _get_clinic_id_from_user(current_user)

    use_case = GetAppointmentUseCase(repo)
    appointment = await use_case.execute(appointment_id, _clinic_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada o no pertenece a tu clínica.",
        )
    return AppointmentReadSchema.model_validate(appointment)


# ---------------------------------------------------------------------------
# POST /appointments
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=AppointmentReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita",
)
async def create_appointment(
    body: AppointmentCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentReadSchema:
    """Crear una nueva cita pendiente.

    - Owner crea citas para sus mascotas
    - Clínica crea citas en nombre de owners
    - Valida disponibilidad del veterinario
    """
    _user_id = _extract_user_id(current_user)
    _clinic_id = _get_clinic_id_from_user(current_user)

    try:
        # Build the AppointmentCreate data object from the request body
        from datetime import datetime as dt

        owner_id_val = (
            body.owner_id if hasattr(body, "owner_id") and body.owner_id else _user_id
        )

        scheduled_start = body.scheduled_start
        if isinstance(scheduled_start, str):
            scheduled_start = dt.fromisoformat(scheduled_start)

        from app.domain.entities.appointment import AppointmentCreate as DomainCreate
        from app.domain.entities.appointment import AppointmentType

        data = DomainCreate(
            pet_id=body.pet_id,
            veterinarian_id=body.veterinarian_id,
            clinic_id=body.clinic_id,
            branch_id=body.branch_id,
            appointment_type=AppointmentType(body.appointment_type),
            scheduled_start=scheduled_start,
            duration_minutes=body.duration_minutes,
            reason=body.reason,
        )

        use_case = CreateAppointmentUseCase(repo)
        appointment = await use_case.execute(
            data=data,
            owner_id=owner_id_val,
            created_by=_user_id,
        )
        return AppointmentReadSchema.model_validate(appointment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# GET /appointments (list by owner or clinic context)
# ---------------------------------------------------------------------------
@router.get(
    "",
    response_model=AppointmentListSchema,
    summary="Listar citas",
)
async def list_appointments(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Elementos por página"),
    status: str | None = Query(None, description="Filtrar por estado"),
    veterinarian_id: int | None = Query(None, description="Filtrar por veterinario"),
    date_from: datetime | None = Query(None, description="Fecha inicio rango"),
    date_to: datetime | None = Query(None, description="Fecha fin rango"),
    my_appointments: bool = Query(
        False, description="Solo citas propias (para owners)"
    ),
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentListSchema:
    """Listar citas según el rol del usuario.

    - Owner: ve sus propias citas (my_appointments=True)
    - Clínica: ve todas las citas de su clínica con filtros opcionales
    """
    user_id = _extract_user_id(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)

    if my_appointments:
        use_case = ListAppointmentsByOwnerUseCase(repo)
        items, total = await use_case.execute(owner_id=user_id, page=page, size=size)
    else:
        use_case = ListAppointmentsByClinicUseCase(repo)
        items, total = await use_case.execute(
            clinic_id=clinic_id,
            page=page,
            size=size,
            status_filter=status,
            veterinarian_id=veterinarian_id,
            date_from=date_from,
            date_to=date_to,
        )

    return AppointmentListSchema(
        items=[AppointmentReadSchema.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


# ---------------------------------------------------------------------------
# PUT /appointments/{appointment_id}
# ---------------------------------------------------------------------------
@router.put(
    "/{appointment_id}",
    response_model=AppointmentReadSchema,
    summary="Actualizar cita",
)
async def update_appointment(
    appointment_id: int,
    body: AppointmentUpdateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentReadSchema:
    """Actualizar una cita existente.

    Solo usuarios con permiso pueden actualizar citas de su clínica.
    """
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = UpdateAppointmentUseCase(repo)
    appointment = await use_case.execute(
        appointment_id=appointment_id,
        clinic_id=clinic_id,
        data=body.model_dump(exclude_none=True),
    )
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada o no pertenece a tu clínica.",
        )
    return AppointmentReadSchema.model_validate(appointment)


# ---------------------------------------------------------------------------
# POST /appointments/{appointment_id}/status
# ---------------------------------------------------------------------------
@router.post(
    "/{appointment_id}/status",
    response_model=AppointmentReadSchema,
    summary="Transicionar estado de cita",
)
async def transition_appointment_status(
    appointment_id: int,
    body: StatusTransitionSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentReadSchema:
    """Transicionar el estado de una cita.

    Transiciones válidas:
    - pending -> approved
    - approved -> confirmed | cancelled
    - confirmed -> completed | no_show | cancelled | rescheduled
    """
    clinic_id = _get_clinic_id_from_user(current_user)

    try:
        use_case = TransitionAppointmentStatusUseCase(repo)
        appointment = await use_case.execute(
            appointment_id=appointment_id,
            clinic_id=clinic_id,
            new_status=body.status.value,
            notes=body.notes,
            scheduled_start=body.scheduled_start,
            duration_minutes=body.duration_minutes,
        )
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada o no pertenece a tu clínica.",
            )
        return AppointmentReadSchema.model_validate(appointment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------------------------
# DELETE /appointments/{appointment_id}
# ---------------------------------------------------------------------------
@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancelar cita",
)
async def cancel_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> None:
    """Cancelar una cita.

    - Owner puede cancelar citas propias pendientes
    - Clínica puede cancelar cualquier cita de su clínica
    """
    clinic_id = _get_clinic_id_from_user(current_user)

    try:
        use_case = TransitionAppointmentStatusUseCase(repo)
        appointment = await use_case.execute(
            appointment_id=appointment_id,
            clinic_id=clinic_id,
            new_status="cancelled",
            notes="Cancelada por usuario",
        )
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cita no encontrada o no pertenece a tu clínica.",
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


# NOTE: GET /appointments/availability se declara ANTES de GET /{appointment_id}
# (ver bloque de rutas) para evitar que "availability" sea capturado como
# appointment_id por la ruta dinámica.
