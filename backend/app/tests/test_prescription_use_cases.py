from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

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
from app.domain.entities.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.domain.entities.consultation import Consultation
from app.domain.entities.prescription import Prescription, PrescriptionCreate


def _completed_appointment(**overrides) -> Appointment:
    defaults = {
        "id": 1,
        "owner_id": 1,
        "pet_id": 1,
        "clinic_id": 1,
        "branch_id": 1,
        "appointment_type": AppointmentType.CONSULTATION,
        "scheduled_start": datetime.now(),
        "scheduled_end": datetime.now() + timedelta(minutes=30),
        "status": AppointmentStatus.COMPLETED,
    }
    defaults.update(overrides)
    return Appointment(**defaults)


def _consultation(**overrides) -> Consultation:
    defaults = {
        "id": 10,
        "appointment_id": 1,
        "pet_id": 1,
        "clinic_id": 1,
        "branch_id": 1,
        "veterinarian_id": 2,
        "history": "",
        "diagnosis": "Vigilante",
        "recommendations": "",
    }
    defaults.update(overrides)
    return Consultation(**defaults)


def _create_data(**overrides) -> PrescriptionCreate:
    defaults = {
        "consultation_id": 10,
        "pet_id": 1,
        "clinic_id": 1,
        "diagnosis": "Deshidratación leve",
        "treatment_notes": "",
        "items": [],
        "treatments": [],
        "reminders": [],
        "created_by": 2,
    }
    defaults.update(overrides)
    return PrescriptionCreate(**defaults)


@pytest.fixture
def prescription_repo():
    return AsyncMock()


@pytest.fixture
def consultation_repo():
    return AsyncMock()


@pytest.fixture
def appointment_repo():
    return AsyncMock()


@pytest.fixture
def create_uc(prescription_repo, consultation_repo, appointment_repo):
    return CreatePrescriptionUseCase(
        prescription_repository=prescription_repo,
        consultation_repository=consultation_repo,
        appointment_repository=appointment_repo,
    )


def _allow_creation(consultation_repo, appointment_repo, prescription_repo):
    consultation_repo.get_by_id.return_value = _consultation()
    appointment_repo.get_by_id.return_value = _completed_appointment()
    prescription_repo.exists_by_consultation.return_value = False
    created = Prescription(
        id=100,
        consultation_id=10,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        veterinarian_id=2,
        diagnosis="Deshidratación leve",
    )
    prescription_repo.create_prescription.return_value = created
    return created


@pytest.mark.asyncio
async def test_create_prescription_success(
    create_uc, prescription_repo, consultation_repo, appointment_repo
):
    _allow_creation(consultation_repo, appointment_repo, prescription_repo)

    result = await create_uc.execute(_create_data())

    assert result.id == 100
    prescription_repo.create_prescription.assert_awaited_once()
    # El uso del veterinario hereda cuando el payload no lo indica.
    sent = prescription_repo.create_prescription.await_args.args[0]
    assert sent.veterinarian_id == 2
    assert sent.branch_id == 1


@pytest.mark.asyncio
async def test_create_prescription_explicit_veterinarian_wins(create_uc):
    consultation_repo = create_uc.consultation_repository
    appointment_repo = create_uc.appointment_repository
    prescription_repo = create_uc.prescription_repository
    consultation_repo.get_by_id.return_value = _consultation()
    appointment_repo.get_by_id.return_value = _completed_appointment()
    prescription_repo.exists_by_consultation.return_value = False
    prescription_repo.create_prescription.return_value = Prescription(
        id=101,
        consultation_id=10,
        pet_id=1,
        clinic_id=1,
        diagnosis="x",
    )

    await create_uc.execute(_create_data(veterinarian_id=77))

    sent = prescription_repo.create_prescription.await_args.args[0]
    assert sent.veterinarian_id == 77


@pytest.mark.asyncio
async def test_create_prescription_invalid_consultation(create_uc, consultation_repo):
    consultation_repo.get_by_id.return_value = None

    with pytest.raises(ConsultationInvalidError):
        await create_uc.execute(_create_data())


@pytest.mark.asyncio
async def test_create_prescription_not_completed(
    create_uc, consultation_repo, appointment_repo
):
    consultation_repo.get_by_id.return_value = _consultation()
    appointment_repo.get_by_id.return_value = _completed_appointment(
        status=AppointmentStatus.CONFIRMED
    )

    with pytest.raises(ConsultationNotCompletedError):
        await create_uc.execute(_create_data())


@pytest.mark.asyncio
async def test_create_prescription_appointment_missing_is_allowed(
    create_uc, consultation_repo, appointment_repo, prescription_repo
):
    consultation_repo.get_by_id.return_value = _consultation()
    appointment_repo.get_by_id.return_value = None
    prescription_repo.exists_by_consultation.return_value = False
    prescription_repo.create_prescription.return_value = Prescription(
        id=102, consultation_id=10, pet_id=1, clinic_id=1, diagnosis="x"
    )

    result = await create_uc.execute(_create_data())

    assert result.id == 102


@pytest.mark.asyncio
async def test_create_prescription_pet_mismatch(
    create_uc, consultation_repo, appointment_repo
):
    consultation_repo.get_by_id.return_value = _consultation(pet_id=5)
    appointment_repo.get_by_id.return_value = _completed_appointment()

    with pytest.raises(OwnershipError):
        await create_uc.execute(_create_data(pet_id=1))


@pytest.mark.asyncio
async def test_create_prescription_duplicate(
    create_uc, consultation_repo, appointment_repo, prescription_repo
):
    consultation_repo.get_by_id.return_value = _consultation()
    appointment_repo.get_by_id.return_value = _completed_appointment()
    prescription_repo.exists_by_consultation.return_value = True

    with pytest.raises(DuplicatePrescriptionError):
        await create_uc.execute(_create_data())


@pytest.mark.asyncio
async def test_get_prescription_found(prescription_repo):
    found = Prescription(id=9, consultation_id=10, pet_id=1, clinic_id=1, diagnosis="x")
    prescription_repo.get_by_id.return_value = found
    uc = GetPrescriptionUseCase(prescription_repo)

    result = await uc.execute(9, clinic_id=1)

    assert result.id == 9
    prescription_repo.get_by_id.assert_awaited_once_with(9, 1)


@pytest.mark.asyncio
async def test_get_prescription_not_found(prescription_repo):
    prescription_repo.get_by_id.return_value = None
    uc = GetPrescriptionUseCase(prescription_repo)

    with pytest.raises(PrescriptionNotFoundError):
        await uc.execute(999, clinic_id=1)


@pytest.mark.asyncio
async def test_list_prescriptions_by_pet(prescription_repo):
    items = [
        Prescription(id=1, consultation_id=10, pet_id=1, clinic_id=1, diagnosis="a"),
        Prescription(id=2, consultation_id=11, pet_id=1, clinic_id=1, diagnosis="b"),
    ]
    prescription_repo.list_by_pet.return_value = (items, 5)
    uc = ListPrescriptionsUseCase(prescription_repo)

    result_items, total = await uc.execute(pet_id=1, clinic_id=1, page=2, size=10)

    assert len(result_items) == 2
    assert total == 5
    prescription_repo.list_by_pet.assert_awaited_once_with(
        pet_id=1, clinic_id=1, page=2, size=10
    )
