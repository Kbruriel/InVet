"""Router FastAPI para citas médicas (BE-008)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.schemas.appointment_schemas import (
    AppointmentCreateSchema,
    AppointmentListSchema,
    AppointmentReadSchema,
    AppointmentUpdateSchema,
    AvailabilityResponseSchema,
    StatusTransitionSchema,
)
from app.application.appointment_use_cases import (
    CreateAppointmentUseCase,
    GetAppointmentUseCase,
    GetAvailabilityUseCase,
    ListAppointmentsByClinicUseCase,
    ListAppointmentsByOwnerUseCase,
    ListAppointmentsByVeterinarianUseCase,
    TransitionAppointmentStatusUseCase,
    UpdateAppointmentUseCase,
)
from app.core.security import get_current_access_user
from app.domain.repositories.appointment_repository import AppointmentRepository


def get_current_db() -> Session:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    return next(_get_db())


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
# GET /appointments/{appointment_id}
# ---------------------------------------------------------------------------
@router.get(
    "/{appointment_id}",
    response_model=AppointmentReadSchema,
    summary="Obtener cita por ID",
)
def get_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentReadSchema:
    """Obtener una cita por ID con validación de tenant."""
    user_id = _extract_user_id(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)

    use_case = GetAppointmentUseCase(repo)
    appointment = use_case.execute(appointment_id, clinic_id)
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
def create_appointment(
    body: AppointmentCreateSchema,
    current_user: dict = Depends(get_current_access_user),
    repo: AppointmentRepository = Depends(get_appointment_repo),
) -> AppointmentReadSchema:
    """Crear una nueva cita pendiente.

    - Owner crea citas para sus mascotas
    - Clínica crea citas en nombre de owners
    - Valida disponibilidad del veterinario
    """
    user_id = _extract_user_id(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)

    try:
        use_case = CreateAppointmentUseCase(repo)
        appointment = use_case.execute(
            data=body,
            owner_id=user_id,  # Asumiendo que el owner_id es user_id para owners
            created_by=user_id,
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
def list_appointments(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(20, ge=1, le=100, description="Elementos por página"),
    status: str | None = Query(None, description="Filtrar por estado"),
    veterinarian_id: int | None = Query(None, description="Filtrar por veterinario"),
    date_from: datetime | None = Query(None, description="Fecha inicio rango"),
    date_to: datetime | None = Query(None, description="Fecha fin rango"),
    my_appointments: bool = Query(False, description="Solo citas propias (para owners)"),
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
        items, total = use_case.execute(owner_id=user_id, page=page, size=size)
    else:
        use_case = ListAppointmentsByClinicUseCase(repo)
        items, total = use_case.execute(
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
def update_appointment(
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
    appointment = use_case.execute(
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
def transition_appointment_status(
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
        appointment = use_case.execute(
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
def cancel_appointment(
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
        appointment = use_case.execute(
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


# ---------------------------------------------------------------------------
# GET /appointments/availability
# ---------------------------------------------------------------------------
@router.get(
    "/availability",
    response_model=AvailabilityResponseSchema,
    summary="Obtener disponibilidad de horarios",
)
def get_appointment_availability(
    date: datetime = Query(..., description="Fecha a consultar (YYYY-MM-DD)"),
    veterinarian_id: int | None = Query(None, description="ID del veterinario (opcional)"),
    clinic_id: int | None = Query(None, description="ID de la clínica"),
    branch_id: int | None = Query(None, description="ID de la sucursal (opcional)"),
    slot_duration: int = Query(30, ge=15, le=120, description="Duración del slot en minutos"),
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

    use_case = GetAvailabilityUseCase(repo)
    slots = use_case.execute(
        veterinarian_id=veterinarian_id,
        clinic_id=clinic_id,
        branch_id=branch_id,
        date=date,
        slot_duration_minutes=slot_duration,
    )

    return AvailabilityResponseSchema(
        date=date.strftime("%Y-%m-%d"),
        slots=[AvailabilitySlotSchema(**s) for s in slots],
        meta={
            "veterinarian_id": veterinarian_id,
            "branch_id": branch_id,
            "slot_duration_minutes": slot_duration,
        },
    )
