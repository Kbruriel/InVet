from unittest.mock import AsyncMock

import pytest

from app.application.use_cases.consultation_use_cases import (
    AppointmentNotCompletedError,
    ConsultationNotFoundError,
    CreateConsultationUseCase,
    DuplicateConsultationError,
    GetConsultationUseCase,
    ListConsultationsUseCase,
    OwnershipError,
)
from app.domain.entities.appointment import AppointmentStatus
from app.domain.entities.consultation import ConsultationCreate


@pytest.fixture
def consultation_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def appointment_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def pet_owner_resolver():
    async def resolver(pet_id, clinic_id):
        return 1  # Always return owner_id 1
    return resolver

@pytest.fixture
def create_consultation_uc(consultation_repo, appointment_repo, pet_owner_resolver):
    return CreateConsultationUseCase(
        consultation_repository=consultation_repo,
        appointment_repository=appointment_repo,
        pet_owner_resolver=pet_owner_resolver,
    )

@pytest.mark.asyncio
async def test_create_consultation_success(create_consultation_uc, consultation_repo, appointment_repo):
    # Arrange
    from datetime import datetime, timedelta

    from app.domain.entities.appointment import Appointment, AppointmentType
    from app.domain.entities.consultation import Consultation

    appointment = Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(),
        scheduled_end=datetime.now() + timedelta(minutes=30),
        status=AppointmentStatus.COMPLETED
    )
    appointment_repo.get_by_id.return_value = appointment

    consultation_data = ConsultationCreate(
        appointment_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        veterinarian_id=1,
        history="test history",
        diagnosis="test diagnosis",
        recommendations="test recommendations",
    )

    consultation_result = Consultation(id=1, appointment_id=1, pet_id=1, clinic_id=1, branch_id=1, history="...", diagnosis="...", recommendations="...")
    consultation_repo.get_by_appointment_id.return_value = None
    consultation_repo.create_consultation.return_value = consultation_result

    # Act
    result = await create_consultation_uc.execute(
        data=consultation_data,
        owner_id=1,
        created_by=1
    )

    # Assert
    assert result.id == 1
    consultation_repo.create_consultation.assert_called_once()

@pytest.mark.asyncio
async def test_create_consultation_derives_branch_and_optional_text(
    consultation_repo,
    appointment_repo,
):
    from datetime import datetime, timedelta

    from app.application.use_cases.consultation_use_cases import (
        CreateConsultationUseCase,
    )
    from app.domain.entities.appointment import Appointment, AppointmentType
    from app.domain.entities.consultation import Consultation

    async def pet_owner_resolver(pet_id, clinic_id):
        return 7

    appointment = Appointment(
        id=2,
        owner_id=7,
        pet_id=9,
        clinic_id=1,
        branch_id=12,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(),
        scheduled_end=datetime.now() + timedelta(minutes=30),
        status=AppointmentStatus.COMPLETED,
    )
    appointment_repo.get_by_id.return_value = appointment
    consultation_repo.get_by_appointment_id.return_value = None
    consultation_repo.create_consultation.return_value = Consultation(
        id=2,
        appointment_id=2,
        pet_id=9,
        clinic_id=1,
        branch_id=12,
        history="",
        diagnosis="Diagnóstico",
        recommendations="",
    )

    uc = CreateConsultationUseCase(
        consultation_repository=consultation_repo,
        appointment_repository=appointment_repo,
        pet_owner_resolver=pet_owner_resolver,
    )
    consultation_data = ConsultationCreate(
        appointment_id=2,
        pet_id=9,
        clinic_id=1,
        diagnosis="Diagnóstico",
    )

    result = await uc.execute(
        data=consultation_data,
        owner_id=None,
        created_by=3,
    )

    created = consultation_repo.create_consultation.call_args.args[0]
    assert created.branch_id == 12
    assert created.history == ""
    assert created.recommendations == ""
    assert result.id == 2

@pytest.mark.asyncio
async def test_create_consultation_appointment_not_completed(create_consultation_uc, appointment_repo):
    # Arrange
    from datetime import datetime, timedelta

    from app.domain.entities.appointment import Appointment, AppointmentType
    appointment = Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(),
        scheduled_end=datetime.now() + timedelta(minutes=30),
        status=AppointmentStatus.PENDING
    )
    appointment_repo.get_by_id.return_value = appointment

    consultation_data = ConsultationCreate(
        appointment_id=1, pet_id=1, clinic_id=1, branch_id=1,
        veterinarian_id=1, history="...", diagnosis="...", recommendations="..."
    )

    # Act & Assert
    with pytest.raises(AppointmentNotCompletedError):
        await create_consultation_uc.execute(data=consultation_data, owner_id=1, created_by=1)

@pytest.mark.asyncio
async def test_create_consultation_appointment_not_found(create_consultation_uc, appointment_repo):
    # Arrange
    appointment_repo.get_by_id.return_value = None

    consultation_data = ConsultationCreate(
        appointment_id=1, pet_id=1, clinic_id=1, branch_id=1,
        veterinarian_id=1, history="...", diagnosis="...", recommendations="..."
    )

    # Act & Assert
    with pytest.raises(OwnershipError):
        await create_consultation_uc.execute(data=consultation_data, owner_id=1, created_by=1)

@pytest.mark.asyncio
async def test_create_consultation_pet_mismatch(create_consultation_uc, appointment_repo):
    # Arrange
    from datetime import datetime, timedelta

    from app.domain.entities.appointment import Appointment, AppointmentType
    appointment = Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(),
        scheduled_end=datetime.now() + timedelta(minutes=30),
        status=AppointmentStatus.COMPLETED
    )
    appointment_repo.get_by_id.return_value = appointment

    consultation_data = ConsultationCreate(
        appointment_id=1, pet_id=2, clinic_id=1, branch_id=1,
        veterinarian_id=1, history="...", diagnosis="...", recommendations="..."
    )

    # Act & Assert
    with pytest.raises(OwnershipError):
        await create_consultation_uc.execute(data=consultation_data, owner_id=1, created_by=1)

@pytest.mark.asyncio
async def test_create_consultation_owner_mismatch(create_consultation_uc, appointment_repo, pet_owner_resolver):
    # Arrange
    from datetime import datetime, timedelta

    from app.domain.entities.appointment import Appointment, AppointmentType
    appointment = Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(),
        scheduled_end=datetime.now() + timedelta(minutes=30),
        status=AppointmentStatus.COMPLETED
    )
    appointment_repo.get_by_id.return_value = appointment

    # Force owner mismatch
    async def wrong_resolver(pet_id, clinic_id):
        return 999

    # We need to re-inject the UC with the wrong resolver or just mock the resolver in the
    # test. Since the fixture provides it, we can't easily change it without recreating the UC.
    from unittest.mock import AsyncMock
    uc = CreateConsultationUseCase(
        consultation_repository=AsyncMock(),
        appointment_repository=appointment_repo,
        pet_owner_resolver=wrong_resolver,
    )

    consultation_data = ConsultationCreate(
        appointment_id=1, pet_id=1, clinic_id=1, branch_id=1,
        veterinarian_id=1, history="...", diagnosis="...", recommendations="..."
    )

    # Act & Assert
    with pytest.raises(OwnershipError):
        await uc.execute(data=consultation_data, owner_id=1, created_by=1)

@pytest.mark.asyncio
async def test_create_consultation_duplicate(create_consultation_uc, appointment_repo):
    # Arrange
    from datetime import datetime, timedelta

    from app.domain.entities.appointment import Appointment, AppointmentType
    appointment = Appointment(
        id=1,
        owner_id=1,
        pet_id=1,
        clinic_id=1,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(),
        scheduled_end=datetime.now() + timedelta(minutes=30),
        status=AppointmentStatus.COMPLETED
    )
    appointment_repo.get_by_id.return_value = appointment

    consultation_data = ConsultationCreate(
        appointment_id=1, pet_id=1, clinic_id=1, branch_id=1,
        veterinarian_id=1, history="...", diagnosis="...", recommendations="..."
    )

    # Mock existing consultation
    from app.domain.entities.consultation import Consultation
    existing_consultation = Consultation(id=100, appointment_id=1, pet_id=1, clinic_id=1, branch_id=1, history="...", diagnosis="...", recommendations="...")
    create_consultation_uc.consultation_repository.get_by_appointment_id.return_value = existing_consultation

    # Act & Assert
    with pytest.raises(DuplicateConsultationError):
        await create_consultation_uc.execute(data=consultation_data, owner_id=1, created_by=1)

@pytest.mark.asyncio
async def test_get_consultation_not_found(consultation_repo):
    # Arrange
    use_case = GetConsultationUseCase(consultation_repo)
    consultation_repo.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ConsultationNotFoundError):
        await use_case.execute(consultation_id=999, clinic_id=1)

@pytest.mark.asyncio
async def test_list_consultations(consultation_repo):
    # Arrange
    use_case = ListConsultationsUseCase(consultation_repo)
    from app.domain.entities.consultation import Consultation

    consultation = Consultation(id=1, appointment_id=1, pet_id=1, clinic_id=1, branch_id=1, history="...", diagnosis="...", recommendations="...")
    consultation_repo.list_by_clinic.return_value = ([consultation], 1)

    # Act
    items, total = await use_case.execute(clinic_id=1, page=1, size=10, pet_id=None)

    # Assert
    assert len(items) == 1
    assert total == 1
    assert items[0].id == 1
