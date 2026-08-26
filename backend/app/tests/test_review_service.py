"""Pruebas de casos de uso de reseÃ±as (BE-012-T06).

Cubre ReviewService: create / respond / get / list_public / list_clinical.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.application.use_cases.review import (
    ReviewError,
    ReviewNotAuthorizedError,
    ReviewNotCompletedError,
    ReviewNotFoundError,
    ReviewRespondDuplicateError,
    ReviewRespondForbiddenError,
    ReviewRespondNotFoundError,
    ReviewDuplicateError as ReviewCreateDuplicateError,
    ReviewService,
)
from app.domain.entities.appointment import (
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.domain.entities.review import (
    Review,
    ReviewCreate,
    ReviewRespond,
    ReviewResponse,
)

CLINIC = 1
OWNER = 50
USER = 100


def _appointment(overrides=None) -> Appointment:
    data = dict(
        id=1,
        owner_id=OWNER,
        pet_id=7,
        clinic_id=CLINIC,
        branch_id=1,
        appointment_type=AppointmentType.CONSULTATION,
        scheduled_start=datetime.now(UTC) - timedelta(days=1),
        scheduled_end=datetime.now(UTC),
        status=AppointmentStatus.COMPLETED,
    )
    if overrides:
        data.update(overrides)
    return Appointment(**data)


def _review(overrides=None) -> Review:
    data = dict(
        id=10,
        appointment_id=1,
        branch_id=1,
        clinic_id=CLINIC,
        user_id=OWNER,
        rating=5,
        comment="Muy buena atenciÃ³n",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    if overrides:
        data.update(overrides)
    return Review(**data)


def _response(review_id: int = 10) -> ReviewResponse:
    return ReviewResponse(
        id=100,
        review_id=review_id,
        branch_id=1,
        user_id=USER,
        body="Gracias por su feedback",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _owner_user(role: str = "owner") -> dict:
    return {"id": USER, "user_id": USER, "role": role, "clinic_id": CLINIC}


@pytest.fixture
def review_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def appointment_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def rating_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(review_repo, appointment_repo, rating_repo) -> ReviewService:
    return ReviewService(review_repo, appointment_repo, rating_repo)


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_success_recalls_rating_summary(
    review_repo, appointment_repo, rating_repo, service
) -> None:
    appointment_repo.get_by_id = AsyncMock(return_value=_appointment())
    review_repo.get_owner_id_by_user = AsyncMock(return_value=OWNER)
    review_repo.exists_by_appointment = AsyncMock(return_value=False)
    review_repo.create = AsyncMock(return_value=_review())
    review_repo.get_review_stats = AsyncMock(
        return_value=(3, {1: 0, 2: 0, 3: 1, 4: 1, 5: 1})
    )

    result = await service.create(
        ReviewCreate(appointment_id=1, rating=5, comment="Ok"),
        _owner_user(),
    )

    assert result.id == 10
    assert result.user_id == OWNER
    appointment_repo.get_by_id.assert_awaited_once_with(1, CLINIC)
    rating_repo.upsert_rating_summary.assert_awaited_once()
    kwargs = rating_repo.upsert_rating_summary.await_args.kwargs
    assert kwargs["total_reviews"] == 3
    assert kwargs["average_rating"] == pytest.approx(4.0)


@pytest.mark.asyncio
async def test_create_appointment_not_completed_raises_422(
    appointment_repo, service
) -> None:
    appointment_repo.get_by_id = AsyncMock(
        return_value=_appointment({"status": AppointmentStatus.PENDING})
    )

    with pytest.raises(ReviewNotCompletedError) as exc:
        await service.create(ReviewCreate(appointment_id=1, rating=5, comment=None), _owner_user())

    assert exc.value.status_code == 422
    appointment_repo.get_by_id.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_appointment_missing_raises_422(appointment_repo, service) -> None:
    appointment_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(ReviewNotCompletedError) as excinfo:
        await service.create(ReviewCreate(appointment_id=1, rating=5, comment=None), _owner_user())

    assert excinfo.value.status_code == 422


@pytest.mark.asyncio
async def test_create_not_owner_raises_403(review_repo, appointment_repo, service) -> None:
    appointment_repo.get_by_id = AsyncMock(return_value=_appointment())
    review_repo.get_owner_id_by_user = AsyncMock(return_value=999)

    with pytest.raises(ReviewNotAuthorizedError) as exc:
        await service.create(ReviewCreate(appointment_id=1, rating=5, comment=None), _owner_user())

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_create_ownerless_user_raises_403(review_repo, appointment_repo, service) -> None:
    appointment_repo.get_by_id = AsyncMock(return_value=_appointment())
    review_repo.get_owner_id_by_user = AsyncMock(return_value=None)

    with pytest.raises(ReviewNotAuthorizedError):
        await service.create(ReviewCreate(appointment_id=1, rating=5, comment=None), _owner_user())


@pytest.mark.asyncio
async def test_create_duplicate_raises_409(review_repo, appointment_repo, service) -> None:
    appointment_repo.get_by_id = AsyncMock(return_value=_appointment())
    review_repo.get_owner_id_by_user = AsyncMock(return_value=OWNER)
    review_repo.exists_by_appointment = AsyncMock(return_value=True)

    with pytest.raises(ReviewCreateDuplicateError) as exc:
        await service.create(ReviewCreate(appointment_id=1, rating=5, comment=None), _owner_user())

    assert exc.value.status_code == 409
    review_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_user_without_clinic_raises_403(service) -> None:
    payload = ReviewCreate(appointment_id=1, rating=5, comment=None)
    with pytest.raises(ReviewError) as exc:
        await service.create(payload, {"id": USER, "user_id": USER, "role": "owner"})

    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# respond
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_respond_success(review_repo, service) -> None:
    review_repo.get_by_id = AsyncMock(return_value=_review())
    review_repo.create_response = AsyncMock(return_value=_response())
    review_repo.get_internal_user_id_by_user = AsyncMock(return_value=None)

    result = await service.respond(
        10, ReviewRespond(body="Respuesta"), _owner_user("veterinarian")
    )

    assert result.response is not None
    assert result.response.body == "Gracias por su feedback"
    sent = review_repo.create_response.await_args.args[0]
    assert sent.review_id == 10
    assert sent.user_id == USER


@pytest.mark.asyncio
async def test_respond_owner_role_forbidden(review_repo, service) -> None:
    review_repo.get_by_id = AsyncMock(return_value=_review())

    with pytest.raises(ReviewRespondForbiddenError) as exc:
        await service.respond(10, ReviewRespond(body="Respuesta"), _owner_user())

    assert exc.value.status_code == 403
    review_repo.create_response.assert_not_awaited()


@pytest.mark.asyncio
async def test_respond_missing_review_404(review_repo, service) -> None:
    review_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(ReviewRespondNotFoundError) as exc:
        await service.respond(
            10, ReviewRespond(body="Respuesta"), _owner_user("staff")
        )

    assert exc.value.status_code == 404
    review_repo.create_response.assert_not_awaited()


@pytest.mark.asyncio
async def test_respond_duplicate_409(review_repo, service) -> None:
    review_repo.get_by_id = AsyncMock(
        return_value=_review(overrides={"response": _response()})
    )

    with pytest.raises(ReviewRespondDuplicateError) as exc:
        await service.respond(
            10, ReviewRespond(body="Respuesta"), _owner_user("admin")
        )

    assert exc.value.status_code == 409
    review_repo.create_response.assert_not_awaited()


# ---------------------------------------------------------------------------
# get / list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_found(review_repo, service) -> None:
    review_repo.get_by_id = AsyncMock(return_value=_review())
    result = await service.get(10, CLINIC)
    assert result.id == 10
    review_repo.get_by_id.assert_awaited_once_with(10, CLINIC)


@pytest.mark.asyncio
async def test_get_missing_raises_404(review_repo, service) -> None:
    review_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(ReviewNotFoundError) as exc:
        await service.get(99, CLINIC)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_public_delegates(review_repo, service) -> None:
    review_repo.list_by_branch = AsyncMock(
        return_value=([_review(), _review(overrides={"id": 11})], 2)
    )
    items, total = await service.list_public(branch_id=1, page=2, page_size=10)

    assert total == 2
    assert [i.id for i in items] == [10, 11]
    review_repo.list_by_branch.assert_awaited_once_with(branch_id=1, page=2, page_size=10)


@pytest.mark.asyncio
async def test_list_clinical_delegates(review_repo, service) -> None:
    review_repo.list_by_clinic = AsyncMock(return_value=([_review()], 1))
    items, total = await service.list_clinical(
        clinic_id=CLINIC, branch_id=2, page=1, page_size=5
    )

    assert total == 1
    review_repo.list_by_clinic.assert_awaited_once_with(
        clinic_id=CLINIC, branch_id=2, page=1, page_size=5
    )

