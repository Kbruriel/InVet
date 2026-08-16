"""Pruebas unitarias para casos de uso de citas médicas (BE-008)."""

import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.domain.entities.appointment import Appointment, AppointmentStatus, AppointmentType


class MockAppointmentRepository:
    """Repositorio en memoria para pruebas."""

    def __init__(self):
        self._items = {}
        self._next_id = 1

    async def get_by_id(self, appointment_id: int, clinic_id: int | None = None) -> Appointment | None:
        appt = self._items.get(appointment_id)
        if appt and appt.clinic_id != clinic_id:
            return None
        return appt

    async def create_appointment(self, appointment: Appointment) -> Appointment:
        if appointment.id is None or appointment.id not in self._items:
            appointment.id = self._next_id
            self._items[appointment.id] = appointment
            self._next_id += 1
        return appointment

    async def update_appointment(self, appointment_id: int, clinic_id: int, updates: dict) -> Appointment | None:
        appt = self._items.get(appointment_id)
        if not appt or appt.clinic_id != clinic_id:
            return None
        for key, value in updates.items():
            if hasattr(appt, key):
                setattr(appt, key, value)
        return appt

    async def transition_status(
        self, appointment_id: int, clinic_id: int, new_status: str, notes: str | None = None,
        scheduled_start: datetime | None = None, duration_minutes: int | None = None
    ) -> Appointment | None:
        appt = self._items.get(appointment_id)
        if not appt or appt.clinic_id != clinic_id:
            return None
        from app.domain.entities.appointment import AppointmentStatus
        appt.status = AppointmentStatus(new_status)
        if notes:
            appt.notes = (appt.notes or "") + f" [{notes}]"
        if scheduled_start is not None:
            appt.scheduled_start = scheduled_start
        if duration_minutes is not None:
            appt.scheduled_end = appt.scheduled_start + timedelta(minutes=duration_minutes)
        return appt

    async def list_by_owner(self, owner_id: int, clinic_id: int, page: int = 1, size: int = 20) -> tuple[list[Appointment], int]:
        items = [a for a in self._items.values() if a.owner_id == owner_id and a.clinic_id == clinic_id]
        total = len(items)
        start = (page - 1) * size
        return items[start : start + size], total

    async def list_by_clinic(self, clinic_id: int, page: int = 1, size: int = 20, **filters) -> tuple[list[Appointment], int]:
        items = [a for a in self._items.values() if a.clinic_id == clinic_id]
        if filters.get("status_filter"):
            from app.domain.entities.appointment import AppointmentStatus
            status_val = filters["status_filter"]
            items = [a for a in items if a.status.value == status_val]
        total = len(items)
        start = (page - 1) * size
        return items[start : start + size], total

    async def list_by_veterinarian(
        self, veterinarian_id: int, clinic_id: int, page: int = 1, size: int = 20
    ) -> tuple[list[Appointment], int]:
        items = [a for a in self._items.values() if a.veterinarian_id == veterinarian_id and a.clinic_id == clinic_id]
        total = len(items)
        start = (page - 1) * size
        return items[start : start + size], total

    async def check_conflict(
        self, veterinarian_id: int, branch_id: int, scheduled_start: datetime, duration_minutes: int
    ) -> bool:
        end_time = scheduled_start + timedelta(minutes=duration_minutes)
        for appt in self._items.values():
            if (
                appt.veterinarian_id == veterinarian_id
                and appt.branch_id == branch_id
                and appt.status not in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED)
                and appt.scheduled_start < end_time
                and appt.scheduled_end > scheduled_start
            ):
                return True
        return False

    async def get_available_slots(
        self, veterinarian_id: int | None, clinic_id: int, branch_id: int, date: datetime, slot_duration_minutes: int
    ) -> list[dict]:
        occupied = []
        for appt in self._items.values():
            if (
                (veterinarian_id is None or appt.veterinarian_id == veterinarian_id)
                and appt.clinic_id == clinic_id
                and appt.branch_id == branch_id
                and appt.scheduled_start.date() == date.date()
                and appt.status not in (AppointmentStatus.CANCELLED,)
            ):
                occupied.append((appt.scheduled_start, appt.scheduled_end))
        return {"occupied": occupied, "date": date}


class TestCreateAppointmentUseCase:
    """Casos de uso para crear citas."""

    @pytest.mark.asyncio
    async def test_creates_appointment_success(self):
        repo = MockAppointmentRepository()
        from app.application.use_cases.appointment_use_cases import CreateAppointmentUseCase
        use_case = CreateAppointmentUseCase(repo)
        start = datetime.now(UTC) + timedelta(days=1)
        appt = await use_case.execute(
            owner_id=1, pet_id=10, clinic_id=1, branch_id=1,
            appointment_type="consultation", scheduled_start=start,
            veterinarian_id=5, reason="Revisión anual"
        )
        assert appt is not None
        assert appt.status == AppointmentStatus.PENDING
        assert appt.appointment_type == AppointmentType.CONSULTATION
        assert appt.duration_minutes == 30
        assert appt.owner_id == 1

    @pytest.mark.asyncio
    async def test_invalid_appointment_type(self):
        repo = MockAppointmentRepository()
        from app.application.use_cases.appointment_use_cases import CreateAppointmentUseCase
        use_case = CreateAppointmentUseCase(repo)
        start = datetime.now(UTC) + timedelta(days=1)
        with pytest.raises(ValueError, match="Tipo de cita inválido"):
            await use_case.execute(
                owner_id=1, pet_id=10, clinic_id=1, branch_id=1,
                appointment_type="invalid_type", scheduled_start=start
            )

    @pytest.mark.asyncio
    async def test_invalid_duration_too_short(self):
        repo = MockAppointmentRepository()
        from app.application.use_cases.appointment_use_cases import CreateAppointmentUseCase
        use_case = CreateAppointmentUseCase(repo)
        start = datetime.now(UTC) + timedelta(days=1)
        with pytest.raises(ValueError, match="La duración debe estar entre 15 y 120 minutos"):
            await use_case.execute(
                owner_id=1, pet_id=10, clinic_id=1, branch_id=1,
                appointment_type="consultation", scheduled_start=start, duration_minutes=10
            )

    @pytest.mark.asyncio
    async def test_conflict_with_veterinarian(self):
        repo = MockAppointmentRepository()
        # Crear primera cita para el veterinario
        start = datetime.now(UTC) + timedelta(days=1, hours=10)
        await repo.create_appointment(Appointment(
            id=99, owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.PENDING,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import CreateAppointmentUseCase
        use_case = CreateAppointmentUseCase(repo)
        with pytest.raises(ValueError, match="El veterinario tiene otro horario"):
            await use_case.execute(
                owner_id=2, pet_id=11, clinic_id=1, branch_id=1,
                appointment_type="consultation", scheduled_start=start, veterinarian_id=5
            )


class TestTransitionAppointmentStatusUseCase:
    """Casos de uso para transición de estados."""

    @pytest.mark.asyncio
    async def test_pending_to_approved(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        appt = await repo.create_appointment(Appointment(
            id=1, owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.PENDING,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        result = await use_case.execute(
            appointment_id=1, clinic_id=1, action="approve", updated_by=2
        )
        assert result.status == AppointmentStatus.APPROVED

    @pytest.mark.asyncio
    async def test_approved_to_confirmed(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.APPROVED,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        result = await use_case.execute(
            appointment_id=1, clinic_id=1, action="confirm", updated_by=3
        )
        assert result.status == AppointmentStatus.CONFIRMED

    @pytest.mark.asyncio
    async def test_confirmed_to_completed(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.CONFIRMED,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        result = await use_case.execute(
            appointment_id=1, clinic_id=1, action="complete", updated_by=5
        )
        assert result.status == AppointmentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_confirmed_to_no_show(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.CONFIRMED,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        result = await use_case.execute(
            appointment_id=1, clinic_id=1, action="no_show", updated_by=5
        )
        assert result.status == AppointmentStatus.NO_SHOW

    @pytest.mark.asyncio
    async def test_invalid_transition_completed_to_approved(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.COMPLETED,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        with pytest.raises(ValueError, match="no es válida para el estado actual"):
            await use_case.execute(
                appointment_id=1, clinic_id=1, action="approve", updated_by=2
            )

    @pytest.mark.asyncio
    async def test_cancel_from_pending(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.PENDING,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        result = await use_case.execute(
            appointment_id=1, clinic_id=1, action="cancel", updated_by=1
        )
        assert result.status == AppointmentStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_nonexistent_appointment(self):
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(MockAppointmentRepository())
        with pytest.raises(ValueError, match="no encontrada"):
            await use_case.execute(appointment_id=999, clinic_id=1, action="approve", updated_by=None)


class TestListAppointmentsByOwnerUseCase:
    """Casos de uso para listar citas."""

    @pytest.mark.asyncio
    async def test_list_owner_appointments(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        for i in range(5):
            await repo.create_appointment(Appointment(
                id=i + 10, owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
                appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.PENDING,
                scheduled_start=start + timedelta(hours=i), scheduled_end=(start + timedelta(hours=i) + timedelta(minutes=30))
            ))
        from app.application.use_cases.appointment_use_cases import ListAppointmentsByOwnerUseCase
        use_case = ListAppointmentsByOwnerUseCase(repo)
        items, total = await use_case.execute(owner_id=1, clinic_id=1, page=1, size=3)
        assert total == 5
        assert len(items) == 3

    @pytest.mark.asyncio
    async def test_empty_list(self):
        from app.application.use_cases.appointment_use_cases import ListAppointmentsByOwnerUseCase
        use_case = ListAppointmentsByOwnerUseCase(MockAppointmentRepository())
        items, total = await use_case.execute(owner_id=999, clinic_id=1, page=1, size=20)
        assert total == 0
        assert len(items) == 0


class TestGetAvailabilityUseCase:
    """Casos de uso para disponibilidad."""

    @pytest.mark.asyncio
    async def test_get_availability_with_slots(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            id=20, owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=1, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.PENDING,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import GetAvailabilityUseCase
        use_case = GetAvailabilityUseCase(repo)
        result = await use_case.execute(
            veterinarian_id=5, clinic_id=1, branch_id=1, date_str=start.strftime("%Y-%m-%d"), slot_duration_minutes=30
        )
        assert "occupied" in result
        assert len(result["occupied"]) == 1


class TestTenantIsolation:
    """Verificar aislamiento por clínica."""

    @pytest.mark.asyncio
    async def test_cannot_access_other_clinic_appointment(self):
        repo = MockAppointmentRepository()
        start = datetime.now(UTC) + timedelta(days=1)
        await repo.create_appointment(Appointment(
            id=30, owner_id=1, pet_id=10, veterinarian_id=5, clinic_id=99, branch_id=1,
            appointment_type=AppointmentType.CONSULTATION, status=AppointmentStatus.PENDING,
            scheduled_start=start, scheduled_end=start + timedelta(minutes=30)
        ))
        from app.application.use_cases.appointment_use_cases import UpdateAppointmentStatusUseCase
        use_case = UpdateAppointmentStatusUseCase(repo)
        # Intentar transicionar con clinic_id diferente (1 vs 99)
        with pytest.raises(ValueError, match="no encontrada"):
            await use_case.execute(appointment_id=30, clinic_id=1, action="approve")
