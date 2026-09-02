"""Router FastAPI para recetas veterinarias (BE-010)."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.schemas.prescription_schemas import (
    PrescriptionCreate,
    PrescriptionPage,
    PrescriptionRead,
    to_domain_create,
)
from app.application.use_cases.prescription_use_cases import (
    ConsultationInvalidError,
    ConsultationNotCompletedError,
    CreatePrescriptionUseCase,
    DuplicatePrescriptionError,
    GetPrescriptionUseCase,
    ListPrescriptionsUseCase,
    OwnershipError,
    PrescriptionNotFoundError,
)
from app.core.security import get_current_access_user
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.consultation_repository import ConsultationRepository
from app.domain.repositories.owner_repository import OwnerRepository, PetRepository
from app.domain.repositories.prescription_repository import PrescriptionRepository
from app.domain.repositories.slice006_repositories import InternalUserRepository

router = APIRouter(prefix="/prescriptions", tags=["prescriptions"])

# Roles que pueden prescribir (rol clínico).
_WRITE_ROLES = {"veterinarian", "clinic", "staff", "admin"}


def get_current_db() -> Generator[Session, None, None]:
    """Dependencia para obtener sesión de base de datos."""
    from app.infrastructure.database.session import get_db as _get_db

    yield from _get_db()


def get_prescription_repo(
    db: Session = Depends(get_current_db),
) -> PrescriptionRepository:
    """Dependencia para el repositorio de recetas (vía factory)."""
    from app.infrastructure.database.repositories.factory import (
        get_prescription_repo as _get,
    )

    return _get(db)


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
    current_user: dict, owner_repo: OwnerRepository
) -> int | None:
    """Resolver el owner vinculado al usuario autenticado, si existe."""
    user_id = _extract_user_id(current_user)
    owner = owner_repo.get_owner_by_user_id(user_id)
    if owner is None:
        return None
    return int(owner.id)


def _require_write_role(current_user: dict) -> None:
    """Validar que el usuario tiene rol clínico para prescribir."""
    role = current_user.get("role")
    if role not in _WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un veterinario o staff de clínica puede prescribir.",
        )


async def _resolve_created_by(
    internal_user_repo: InternalUserRepository, user_id: int, clinic_id: int
) -> int | None:
    """``prescriptions.created_by`` referencia ``internal_users.id``."""
    internal_user = await internal_user_repo.get_by_user_id(user_id, clinic_id)
    return internal_user.id if internal_user else None


def _assert_owner_pet(pet_repo: PetRepository, pet_id: int, owner_id: int) -> None:
    """Validar que la mascota pertenece al owner; si no, 404."""
    pet = pet_repo.get_pet_by_id(pet_id)
    if pet is None or pet.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La receta no existe.",
        )


# ---------------------------------------------------------------------------
# POST /prescriptions — crear receta (vet/staff/clinica)
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=PrescriptionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar receta veterinaria para una consulta completada",
)
async def create_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_current_db),
    current_user: dict = Depends(get_current_access_user),
    prescription_repo: PrescriptionRepository = Depends(get_prescription_repo),
    consultation_repo: ConsultationRepository = Depends(get_consultation_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    internal_user_repo: InternalUserRepository = Depends(get_internal_user_repo),
) -> PrescriptionRead:
    """Registrar una receta para una consulta en estado ``completed``.

    - Solo roles clínicos (veterinarian/staff/admin) pueden crear (403).
    - La consulta debe existir en la clínica del usuario (BOLA/IDOR → 404).
    - La cita debe estar ``completed`` (422).
    - No se permiten duplicados por consulta (409).
    """
    _require_write_role(current_user)
    clinic_id = _get_clinic_id_from_user(current_user)
    user_id = _extract_user_id(current_user)
    created_by = await _resolve_created_by(internal_user_repo, user_id, clinic_id)

    use_case = CreatePrescriptionUseCase(
        prescription_repository=prescription_repo,
        consultation_repository=consultation_repo,
        appointment_repository=appointment_repo,
    )

    domain_data = to_domain_create(payload, clinic_id, created_by)

    try:
        result = await use_case.execute(data=domain_data)
    except ConsultationInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        ) from None
    except ConsultationNotCompletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message
        ) from None
    except DuplicatePrescriptionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=exc.message
        ) from None
    except OwnershipError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=exc.message
        ) from None

    # BE-013-T06: emit notificacion al owner tras receta creada
    from app.api.v1.routers._notify import emit_notify
    from app.infrastructure.database.models.owner import Owner
    from app.infrastructure.database.models.pet import Pet

    try:
        pet = getattr(result, "pet", None)
        pet_obj = (
            db.query(Pet).filter(Pet.id == pet.id if pet else 0).first()
            if pet
            else None
        )
        pet_display = (
            getattr(pet_obj, "name", str(payload.pet_id)) if pet_obj else "mascota"
        )
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
                event_type="prescription_created",
                ref_entity="prescription",
                ref_id=result.id,
                body_extra=f"Receta veterinaria registrada | Mascota: {pet_display}",
            )
    except Exception:
        # BE-013: un fallo de notificacion no debe romper la creacion de la receta.
        pass

    return PrescriptionRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /prescriptions/{id} — obtener detalle
# ---------------------------------------------------------------------------
@router.get(
    "/{prescription_id}",
    response_model=PrescriptionRead,
    summary="Obtener detalle de una receta",
)
async def get_prescription(
    prescription_id: int,
    current_user: dict = Depends(get_current_access_user),
    prescription_repo: PrescriptionRepository = Depends(get_prescription_repo),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo: OwnerRepository = Depends(get_owner_repo),
) -> PrescriptionRead:
    """Obtener detalle de una receta específica.

    - Solo usuarios de la misma clínica pueden verla (404).
    - Si el usuario es propietario, solo ve recetas de sus mascotas (404).
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    owner_id = _get_owner_id_from_user(current_user, owner_repo)
    use_case = GetPrescriptionUseCase(prescription_repo)

    try:
        result = await use_case.execute(prescription_id, clinic_id)
    except PrescriptionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.message
        ) from None

    if owner_id is not None:
        _assert_owner_pet(pet_repo, result.pet_id, owner_id)

    return PrescriptionRead.model_validate(result)


# ---------------------------------------------------------------------------
# GET /prescriptions — listado paginado por mascota
# ---------------------------------------------------------------------------
@router.get(
    "",
    response_model=PrescriptionPage,
    summary="Listar recetas de una mascota con paginación",
)
async def list_prescriptions(
    pet_id: int = Query(..., gt=0, description="ID de la mascota"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(
        20, ge=1, le=100, alias="page_size", description="Tamaño de página"
    ),
    current_user: dict = Depends(get_current_access_user),
    prescription_repo: PrescriptionRepository = Depends(get_prescription_repo),
    pet_repo: PetRepository = Depends(get_pet_repo),
    owner_repo: OwnerRepository = Depends(get_owner_repo),
) -> PrescriptionPage:
    """Listado paginado de recetas de una mascota.

    - ``pet_id`` es obligatorio.
    - Solo usuarios de la misma clínica (tenant isolation).
    - Si el usuario es propietario, la mascota debe ser de su propiedad (404).
    """
    clinic_id = _get_clinic_id_from_user(current_user)
    owner_id = _get_owner_id_from_user(current_user, owner_repo)

    if owner_id is not None:
        _assert_owner_pet(pet_repo, pet_id, owner_id)

    use_case = ListPrescriptionsUseCase(prescription_repo)
    items, total = await use_case.execute(
        pet_id=pet_id, clinic_id=clinic_id, page=page, size=page_size
    )

    return PrescriptionPage(
        items=[PrescriptionRead.model_validate(i) for i in items],
        meta={
            "page": page,
            "page_size": page_size,
            "size": len(items),
            "total": total,
            "pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    )
