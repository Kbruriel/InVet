"""Router FastAPI para consultas médicas (BE-009)."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.consultation_schemas import (
    ConsultationCreate,
    ConsultationPage,
    ConsultationRead,
)
from app.application.use_cases.consultation_use_cases import (
    AppointmentNotCompletedError,
    ConsultationNotFoundError,
    CreateConsultationUseCase,
    DuplicateConsultationError,
    GetConsultationUseCase,
    ListConsultationsUseCase,
    OwnershipError,
)
from app.core.security import get_current_access_user
from app.domain.entities.consultation import (
    ConsultationCreate as ConsultationCreateDomain,
)
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.consultation_repository import ConsultationRepository
from app.domain.repositories.owner_repository import OwnerRepository, PetRepository
from app.domain.repositories.slice006_repositories import InternalUserRepository

router = APIRouter(prefix="/consultations", tags=["consultations"])

# Roles que pueden registrar una consulta (rol clínico).
_WRITE_ROLES = {"veterinarian", "clinic", "staff", "admin"}


def get_current_db() -> Generator[Session, None, None]:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    yield from _get_db()


def get_consultation_repo(
    db: Session = Depends(get_current_db),
) -> ConsultationRepository:
    """Dependencia para el repositorio de consultas (vía factory)."""
    from app.infrastructure.database.repositories.factory import (
        get_consultation_repo as _get,
    )

    return _get(db)


def get_appointment_repo(
    db: Session = Depends(get_current_db),
) -> AppointmentRepository:
    """Dependencia para el repositorio de citas (vía factory)."""
    from app.infrastructure.database.repositories.factory import (
        get_appointment_repo as _get,
    )

    return _get(db)


def get_pet_repo(
    db: Session = Depends(get_current_db),
) -> PetRepository:
    """Dependencia para el repositorio de mascotas (ownership checks)."""
    from app.infrastructure.database.repositories.factory import get_pet_repo as _get

    return _get(db)


def get_owner_repo(
    db: Session = Depends(get_current_db),
) -> OwnerRepository:
    """Dependencia para el repositorio de propietarios."""
    from app.infrastructure.database.repositories.factory import get_owner_repo as _get

    return _get(db)


def get_internal_user_repo(
    db: Session = Depends(get_current_db),
) -> InternalUserRepository:
    """Dependencia para el repositorio de usuarios internos (resolución ``created_by``)."""
    from app.infrastructure.database.repositories.factory import (
        get_internal_user_repo as _get,
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


def _get_owner_id_from_user(
    current_user: dict,
    owner_repo: OwnerRepository,
) -> int | None:
    """Resolver el owner vinculado al usuario autenticado, si existe."""
    user_id = _extract_user_id(current_user)
    owner = owner_repo.get_owner_by_user_id(user_id)
    if owner is None:
        return None
    return int(owner.id)


def _require_write_role(current_user: dict) -> None:
    """Validar que el usuario tiene rol clínico para registrar consultas."""
    role = current_user.get("role")
    if role not in _WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un veterinario o staff de clínica puede registrar consultas.",
        )


async def _resolve_created_by(
    internal_user_repo: InternalUserRepository, user_id: int, clinic_id: int
) -> int | None:
    """``consultations.created_by`` referencia ``internal_users.id`` (no ``users.id``).

    Resuelve el usuario interno vinculado al ``user_id`` autenticado dentro de la
    clínica del tenant, o ``None`` cuando el usuario es un propietario/externo
    sin registro interno.
    """
    internal_user = await internal_user_repo.get_by_user_id(user_id, clinic_id)
    return internal_user.id if internal_user else None


def _build_pet_owner_resolver(pet_repo: PetRepository):
    """Construye una función async que resuelve el owner de una mascota."""

    async def _resolve(pet_id: int, clinic_id: int) -> int | None:
        pet = pet_repo.get_pet_by_id(pet_id)
        if pet is None:
            return None
        return pet.owner_id

    return _resolve


# ---------------------------------------------------------------------------
# POST /consultations — registrar consulta (vet/staff/clinica)
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=ConsultationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar consulta médica para una cita completada",
)
async def create_consultation(
    payload: ConsultationCreate,
    db: Session = Depends(get_current_db),
    current_user: dict = Depends(get_current_access_user),
    consultation_repo: ConsultationRepository = Depends(get_consultation_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    pet_repo: PetRepository = Depends(get_pet_repo),
    internal_user_repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> ConsultationRead:
    """Registrar una consulta para una cita en estado ``completed``.

    - Solo roles clínicos (veterinarian/staff/admin) pueden crear (403).
    - La cita debe existir en la clínica del usuario (BOLA/IDOR).
    - La cita debe estar ``completed`` (422).
    - No se permiten duplicados por cita (409).
    """
    _require_write_role(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)
    user_id = _extract_user_id(current_user)
    created_by = await _resolve_created_by(internal_user_repo, user_id, clinic_id)

    use_case = CreateConsultationUseCase(
        consultation_repository=consultation_repo,
        appointment_repository=appointment_repo,
        pet_owner_resolver=_build_pet_owner_resolver(pet_repo),
    )

    domain_data = ConsultationCreateDomain(
        appointment_id=payload.appointment_id,
        pet_id=payload.pet_id,
        clinic_id=clinic_id,
        branch_id=payload.branch_id,
        veterinarian_id=payload.veterinarian_id,
        history=payload.history,
        diagnosis=payload.diagnosis,
        recommendations=payload.recommendations,
    )

    try:
        result = await use_case.execute(
            data=domain_data,
            created_by=created_by,
        )
    except AppointmentNotCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        ) from None
    except DuplicateConsultationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=exc.message
        ) from None
    except OwnershipError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=exc.message
        ) from None

    # BE-013-T06: emit notificacion al owner tras consulta completada
    from app.api.v1.routers._notify import emit_notify
    try:
        pet = pet_repo.get_pet_by_id(payload.pet_id)
        pet_display = getattr(pet, "name", str(payload.pet_id)) if pet else str(payload.pet_id)
        owner_id_for_pet = None
        owner_email = None
        if pet:
            from app.infrastructure.database.models.owner import Owner as OwnerModel
            owner = db.query(OwnerModel).filter(OwnerModel.id == pet.owner_id).first()
            if owner:
                owner_id_for_pet = int(owner.user_id)
                owner_email = owner.email
        if owner_id_for_pet:
            await emit_notify(
                db=db,
                recipient_user_id=owner_id_for_pet,
                recipient_email=owner_email,
                clinic_id=clinic_id,
                event_type="consultation_completed",
                ref_entity="consultation",
                ref_id=result.id if result else 0,
                body_extra=f"Clinica: {payload.diagnosis[:80] if payload.diagnosis else 'Sin diagnostico'} | Mascota: {pet_display}",
            )
    except Exception:
        # BE-013: un fallo de notificacion no debe romper la consulta.
        pass

    return ConsultationRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /consultations/{id} — obtener detalle
# ---------------------------------------------------------------------------
@router.get(
    "/{consultation_id}",
    response_model=ConsultationRead,
    summary="Obtener detalle de una consulta",
)
async def get_consultation(
    consultation_id: int,
    current_user: dict = Depends(get_current_access_user),
    consultation_repo: ConsultationRepository = Depends(get_consultation_repo),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo: OwnerRepository = Depends(get_owner_repo),
) -> ConsultationRead:
    """Obtener detalle de una consulta específica.

    - Solo usuarios de la misma clínica pueden verla (403/404).
    - Si el usuario es propietario, solo ve consultas de sus mascotas.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    owner_id = _get_owner_id_from_user(current_user, owner_repo)
    use_case = GetConsultationUseCase(consultation_repo)

    try:
        result = await use_case.execute(consultation_id, clinic_id)
    except ConsultationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from None

    if owner_id is not None:
        pet = pet_repo.get_pet_by_id(result.pet_id)
        if pet is None or pet.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La consulta no existe.",
            )

    return ConsultationRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /consultations — listado paginado con filtros (T08)
# ---------------------------------------------------------------------------
@router.get(
    "",
    response_model=ConsultationPage,
    summary="Listar consultas médicas con paginación",
)
async def list_consultations(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(
        20, ge=1, le=100, alias="page_size", description="Tamaño de página"
    ),
    pet_id: int | None = Query(None, gt=0, description="Filtrar por mascota (opcional)"),
    current_user: dict = Depends(get_current_access_user),
    consultation_repo: ConsultationRepository = Depends(get_consultation_repo),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo: OwnerRepository = Depends(get_owner_repo),
) -> ConsultationPage:
    """Listado paginado de consultas médicas.

    - Solo usuarios de la misma clínica pueden verlas (tenant isolation).
    - Permite filtrar por ``pet_id`` cuando el caller conoce la mascota.
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    owner_id = _get_owner_id_from_user(current_user, owner_repo)

    if owner_id is not None:
        if pet_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="pet_id es obligatorio para consultar el historial del propietario.",
            )

        pet = pet_repo.get_pet_by_id(pet_id)
        if pet is None or pet.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La mascota no existe.",
            )

        items, total = await consultation_repo.list_by_pet(
            pet_id=pet_id,
            clinic_id=clinic_id,
            page=page,
            size=page_size,
        )
    else:
        use_case = ListConsultationsUseCase(consultation_repo)
        items, total = await use_case.execute(
            clinic_id=clinic_id,
            page=page,
            size=page_size,
            pet_id=pet_id,
        )

    return ConsultationPage(
        items=[ConsultationRead.model_validate(i) for i in items],
        meta={
            "page": page,
            "page_size": page_size,
            "size": len(items),
            "total": total,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    )
