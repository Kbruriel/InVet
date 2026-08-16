"""Implementación del repositorio de citas médicas para BE-008."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.entities.appointment import Appointment
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.infrastructure.database.models.appointment import (
    Appointment as AppointmentModel,
    _AppointmentStatus,
    _AppointmentType,
)


def _domain_from_model(model: AppointmentModel) -> Appointment:
    """Convierte un modelo ORM a entidad de dominio."""
    return Appointment(
        id=model.id,
        owner_id=model.owner_id,
        pet_id=model.pet_id,
        veterinarian_id=model.veterinarian_id,
        clinic_id=model.clinic_id,
        branch_id=model.branch_id,
        appointment_type=_AppointmentType(model.appointment_type.value),
        status=_AppointmentStatus(model.status.value),
        scheduled_start=model.scheduled_start,
        scheduled_end=model.scheduled_end,
        duration_minutes=model.duration_minutes,
        reason=model.reason,
        notes=model.notes,
        created_by=model.created_by,
        updated_at=model.updated_at,
    )


class AppointmentRepositoryImpl(AppointmentRepository):
    """Implementación concreta del repositorio de citas."""

    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_by_id(self, appointment_id: int, clinic_id: int) -> Appointment | None:
        """Obtener una cita por ID y clinic_id con tenant isolation."""
        stmt = (
            select(AppointmentModel)
            .where(AppointmentModel.id == appointment_id)
            .where(AppointmentModel.clinic_id == clinic_id)
        )
        result = self.db.execute(stmt).scalar_one_or_none()
        if result is None:
            return None
        return _domain_from_model(result)

    async def create_appointment(self, appointment: Appointment) -> Appointment:
        """Crear una nueva cita."""
        model = AppointmentModel(
            owner_id=appointment.owner_id,
            pet_id=appointment.pet_id,
            veterinarian_id=appointment.veterinarian_id,
            clinic_id=appointment.clinic_id,
            branch_id=appointment.branch_id,
            appointment_type=_AppointmentType(appointment.appointment_type.value),
            status=_AppointmentStatus.PENDING,
            scheduled_start=appointment.scheduled_start,
            scheduled_end=appointment.scheduled_end,
            duration_minutes=appointment.duration_minutes,
            reason=appointment.reason,
            notes=appointment.notes,
            created_by=appointment.created_by,
        )
        self.db.add(model)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def update_appointment(
        self, appointment_id: int, clinic_id: int, data: dict[str, Any]
    ) -> Appointment | None:
        """Actualizar campos de una cita existente."""
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == appointment_id,
            AppointmentModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        updatable_fields = [
            "veterinarian_id",
            "scheduled_start",
            "scheduled_end",
            "duration_minutes",
            "reason",
            "notes",
        ]
        for field in updatable_fields:
            if field in data and data[field] is not None:
                setattr(model, field, data[field])

        model.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def transition_status(
        self,
        appointment_id: int,
        clinic_id: int,
        new_status: str,
        notes: str | None = None,
        scheduled_start: datetime | None = None,
        duration_minutes: int | None = None,
    ) -> Appointment | None:
        """Transicionar el estado de una cita."""
        stmt = select(AppointmentModel).where(
            AppointmentModel.id == appointment_id,
            AppointmentModel.clinic_id == clinic_id,
        )
        model = self.db.execute(stmt).scalar_one_or_none()
        if model is None:
            return None

        model.status = _AppointmentStatus(new_status)
        if notes is not None:
            model.notes = notes
        if scheduled_start is not None:
            model.scheduled_start = scheduled_start
            model.scheduled_end = scheduled_start + timedelta(
                minutes=(duration_minutes or model.duration_minutes)
            )
        if duration_minutes is not None:
            model.duration_minutes = duration_minutes
            model.scheduled_end = model.scheduled_start + timedelta(
                minutes=duration_minutes
            )
        model.updated_at = datetime.now(UTC)
        self.db.flush()
        self.db.refresh(model)
        return _domain_from_model(model)

    async def list_by_owner(
        self,
        owner_id: int,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un propietario con paginación."""
        base_stmt = select(AppointmentModel).where(
            AppointmentModel.owner_id == owner_id
        ).order_by(AppointmentModel.scheduled_start.desc())

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        paginated_stmt = base_stmt.offset(offset).limit(size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total

    async def list_by_clinic(
        self,
        clinic_id: int,
        page: int = 1,
        size: int = 20,
        status_filter: str | None = None,
        veterinarian_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de una clínica con filtros y paginación."""
        conditions = [AppointmentModel.clinic_id == clinic_id]

        if status_filter:
            conditions.append(AppointmentModel.status == _AppointmentStatus(status_filter))
        if veterinarian_id is not None:
            conditions.append(AppointmentModel.veterinarian_id == veterinarian_id)
        if date_from is not None:
            conditions.append(AppointmentModel.scheduled_start >= date_from)
        if date_to is not None:
            # Incluyendo todo el día final
            date_to_end = date_to.replace(hour=23, minute=59, second=59)
            conditions.append(AppointmentModel.scheduled_start <= date_to_end)

        base_stmt = (
            select(AppointmentModel)
            .where(*conditions)
            .order_by(AppointmentModel.scheduled_start.desc())
        )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        paginated_stmt = base_stmt.offset(offset).limit(size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total

    async def list_by_veterinarian(
        self,
        veterinarian_id: int,
        page: int = 1,
        size: int = 20,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[Appointment], int]:
        """Listar citas de un veterinario con filtros."""
        conditions = [AppointmentModel.veterinarian_id == veterinarian_id]

        if date_from is not None:
            conditions.append(AppointmentModel.scheduled_start >= date_from)
        if date_to is not None:
            date_to_end = date_to.replace(hour=23, minute=59, second=59)
            conditions.append(AppointmentModel.scheduled_start <= date_to_end)

        base_stmt = (
            select(AppointmentModel)
            .where(*conditions)
            .order_by(AppointmentModel.scheduled_start.desc())
        )

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        offset = (page - 1) * size
        paginated_stmt = base_stmt.offset(offset).limit(size)
        results = self.db.execute(paginated_stmt).scalars().all()
        return [_domain_from_model(r) for r in results], total

    async def check_conflict(
        self,
        veterinarian_id: int,
        branch_id: int,
        scheduled_start: datetime,
        duration_minutes: int = 30,
        exclude_appointment_id: int | None = None,
    ) -> bool:
        """Verificar si existe un conflicto de horario para un veterinario."""
        scheduled_end = scheduled_start + timedelta(minutes=duration_minutes)

        conditions = [
            AppointmentModel.veterinarian_id == veterinarian_id,
            AppointmentModel.branch_id == branch_id,
            AppointmentModel.status.notin_(
                [_AppointmentStatus.CANCELLED, _AppointmentStatus.COMPLETED]
            ),
            AppointmentModel.scheduled_start < scheduled_end,
            AppointmentModel.scheduled_end > scheduled_start,
        ]

        if exclude_appointment_id is not None:
            conditions.append(AppointmentModel.id != exclude_appointment_id)

        stmt = select(AppointmentModel).where(*conditions).limit(1)
        result = self.db.execute(stmt).scalar_one_or_none()
        return result is not None

    async def get_available_slots(
        self,
        veterinarian_id: int | None,
        clinic_id: int,
        branch_id: int | None,
        date: datetime,
        slot_duration_minutes: int = 30,
    ) -> list[dict]:
        """Obtener slots disponibles para un veterinario/clínica en una fecha."""
        # Obener todas las citas existentes en esa fecha
        date_end = date.replace(hour=23, minute=59, second=59)

        conditions = [
            AppointmentModel.clinic_id == clinic_id,
            AppointmentModel.scheduled_start >= date,
            AppointmentModel.scheduled_start <= date_end,
            AppointmentModel.status != _AppointmentStatus.CANCELLED,
        ]

        if veterinarian_id is not None:
            conditions.append(AppointmentModel.veterinarian_id == veterinarian_id)
        if branch_id is not None:
            conditions.append(AppointmentModel.branch_id == branch_id)

        stmt = select(AppointmentModel).where(*conditions)
        results = self.db.execute(stmt).scalars().all()

        # Construir slots de trabajo (ej: 8:00 - 18:00)
        work_start_hour = 8
        work_end_hour = 18
        slots = []

        current = date.replace(hour=work_start_hour, minute=0, second=0, microsecond=0)
        end_time = date.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

        booked_slots: dict[int | None, list[tuple[datetime, datetime]]] = {}
        for r in results:
            key = r.veterinarian_id
            if key not in booked_slots:
                booked_slots[key] = []
            booked_slots[key].append((r.scheduled_start, r.scheduled_end))

        while current < end_time:
            slot_end = current + timedelta(minutes=slot_duration_minutes)
            for vet_id, bookings in booked_slots.items():
                for b_start, b_end in bookings:
                    if not (slot_end <= b_start or current >= b_end):
                        slots.append({
                            "start": current,
                            "end": slot_end,
                            "is_available": False,
                            "veterinarian_id": vet_id,
                            "reason": "Cita existente",
                        })
                        break
                else:
                    continue
                break
            else:
                available_vets = list(booked_slots.keys()) + ([None] if None not in booked_slots else [])
                for vid in set(available_vets):
                    slots.append({
                        "start": current,
                        "end": slot_end,
                        "is_available": True,
                        "veterinarian_id": vid,
                    })
                break

            current = slot_end

        return slots
