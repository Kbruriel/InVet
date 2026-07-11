"""
Routers para la gestion de citas.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.appointment_schemas import (
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentSlotResponse,
)
from app.application.appointment.use_cases import (
    CancelAppointmentUseCase,
    CompleteAppointmentUseCase,
    ConfirmAppointmentUseCase,
    CreateAppointmentUseCase,
    GetAvailableSlotsUseCase,
    GetUserAppointmentsUseCase,
    MarkNoShowUseCase,
    RescheduleAppointmentUseCase,
)
from app.core.security import get_current_user
from app.domain.entities.appointment import AppointmentCreate
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.appointment_repository_impl import (
    AppointmentRepositoryImpl,
    AppointmentSlotRepositoryImpl,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


def get_appointment_repo(db: Session = Depends(get_db)):
    return AppointmentRepositoryImpl(db)


def get_slot_repo(db: Session = Depends(get_db)):
    return AppointmentSlotRepositoryImpl(db)


def _ensure_owner_access(current_user: dict, owner_id: int) -> None:
    if current_user.get("id") != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta cita",
        )


def _ensure_appointment_access(current_user: dict, appointment_owner_id: int) -> None:
    if current_user.get("id") != appointment_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta cita",
        )


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Crear una nueva cita."""
    try:
        _ensure_owner_access(current_user, appointment_data.owner_id)
        repo = get_appointment_repo(db)
        slot_repo = get_slot_repo(db)
        use_case = CreateAppointmentUseCase(repo, slot_repo)
        payload = AppointmentCreate(**appointment_data.model_dump())
        return use_case.execute(payload)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Obtener detalles de una cita."""
    try:
        repo = get_appointment_repo(db)
        appointment = repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        _ensure_appointment_access(current_user, appointment.owner_id)
        return appointment
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Cancelar una cita existente."""
    try:
        repo = get_appointment_repo(db)
        slot_repo = get_slot_repo(db)
        appointment = repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        _ensure_appointment_access(current_user, appointment.owner_id)

        use_case = CancelAppointmentUseCase(repo, slot_repo)
        result = use_case.execute(appointment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Confirmar una cita existente."""
    try:
        repo = get_appointment_repo(db)
        appointment = repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        _ensure_appointment_access(current_user, appointment.owner_id)

        use_case = ConfirmAppointmentUseCase(repo)
        result = use_case.execute(appointment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int,
    new_slot_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Reprogramar una cita existente."""
    try:
        repo = get_appointment_repo(db)
        slot_repo = get_slot_repo(db)
        appointment = repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        _ensure_appointment_access(current_user, appointment.owner_id)

        use_case = RescheduleAppointmentUseCase(repo, slot_repo)
        result = use_case.execute(appointment_id, new_slot_id)
        if not result:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{appointment_id}/no-show", response_model=AppointmentResponse)
async def mark_no_show(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Marcar una cita como no-show."""
    try:
        repo = get_appointment_repo(db)
        appointment = repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        _ensure_appointment_access(current_user, appointment.owner_id)

        use_case = MarkNoShowUseCase(repo)
        result = use_case.execute(appointment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.put("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Completar una cita."""
    try:
        repo = get_appointment_repo(db)
        appointment = repo.find_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        _ensure_appointment_access(current_user, appointment.owner_id)

        use_case = CompleteAppointmentUseCase(repo)
        result = use_case.execute(appointment_id)
        if not result:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return result
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get("/users/{user_id}/appointments", response_model=AppointmentListResponse)
async def get_user_appointments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Obtener las citas de un usuario."""
    try:
        _ensure_owner_access(current_user, user_id)
        repo = get_appointment_repo(db)
        use_case = GetUserAppointmentsUseCase(repo)
        appointments = use_case.execute(user_id)
        return AppointmentListResponse(
            appointments=appointments,
            total=len(appointments),
            page=1,
            per_page=len(appointments),
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@router.get(
    "/clinics/{clinic_id}/branches/{branch_id}/availability",
    response_model=list[AppointmentSlotResponse],
)
async def get_available_slots(
    clinic_id: int,
    branch_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Obtener franjas horarias disponibles para una clinica y sucursal."""
    try:
        slot_repo = get_slot_repo(db)
        use_case = GetAvailableSlotsUseCase(slot_repo)
        return use_case.execute(clinic_id, branch_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
