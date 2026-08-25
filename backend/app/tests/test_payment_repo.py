"""Pruebas del repositorio de pagos operativos (BE-011-T03)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.data.payment_repo import get_payment_repo
from app.domain.entities.payment import Payment, PaymentMethod, PaymentStatus
from app.infrastructure.database.models.appointment import Appointment
from app.infrastructure.database.models.branch import Branch
from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.owner import Owner
from app.infrastructure.database.models.pet import Pet
from app.infrastructure.database.models.service_model import Service


def _seed_tenant(db, clinic_name: str):
    """Crea un paciente (owner+pet), clinica, sucursal, servicio y una cita."""
    owner = Owner(first_name="A", last_name=clinic_name, email=f"{clinic_name}@t.io")
    db.add(owner)
    db.flush()
    pet = Pet(owner_id=owner.id, name="Kiko", species="canino")
    db.add(pet)
    db.flush()
    clinic = Clinic(
        name=clinic_name,
        address="Calle 1",
        city="CDMX",
        state="CDMX",
        country="MX",
        postal_code="00000",
    )
    db.add(clinic)
    db.flush()
    branch = Branch(
        clinic_id=clinic.id,
        name=f"{clinic_name}-B1",
        address="Calle 2",
        city="CDMX",
        state="CDMX",
        country="MX",
        postal_code="00000",
    )
    db.add(branch)
    db.flush()
    service = Service(
        branch_id=branch.id,
        clinic_id=clinic.id,
        name="Consulta",
        price=10000,
        duration_minutes=30,
    )
    db.add(service)
    db.flush()
    start = datetime.now(UTC)
    appointment = Appointment(
        owner_id=owner.id,
        pet_id=pet.id,
        clinic_id=clinic.id,
        branch_id=branch.id,
        scheduled_start=start,
        scheduled_end=start + timedelta(minutes=30),
    )
    db.add(appointment)
    db.flush()
    return appointment.id, service.id, clinic.id


def _payment(appt, svc, clinic, method=PaymentMethod.CASH):
    return Payment(
        appointment_id=appt,
        service_id=svc,
        clinic_id=clinic,
        amount=10000,
        method=method,
        amount_received=10000 if method == PaymentMethod.CASH else None,
        change_amount=0 if method == PaymentMethod.CASH else None,
        status=PaymentStatus.PAID,
        paid_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_create_and_get_by_id_with_tenant_isolation(db_session):
    appt, svc, clinic = _seed_tenant(db_session, "alpha")
    repo = get_payment_repo(db_session)

    created = await repo.create(_payment(appt, svc, clinic))
    assert created.id is not None
    assert created.status == PaymentStatus.PAID

    fetched = await repo.get_by_id(created.id, clinic)
    assert fetched is not None
    assert fetched.appointment_id == appt

    # Tenant isolation: otra clinic no debe ver el pago
    other = await repo.get_by_id(created.id, 999999)
    assert other is None


@pytest.mark.asyncio
async def test_list_filters_tenant_date_status_and_pagination(db_session):
    appt, svc, clinic = _seed_tenant(db_session, "beta")
    repo = get_payment_repo(db_session)

    now = datetime.now(UTC)
    p1 = _payment(appt, svc, clinic)
    p1.paid_at = now - timedelta(days=30)
    await repo.create(p1)

    p2 = _payment(appt, svc, clinic)
    p2.paid_at = now
    created2 = await repo.create(p2)

    # Listado del tenant: 2 pagos + paginacion
    items, total = await repo.list(clinic_id=clinic)
    assert total == 2
    assert len(items) == 2

    items, total = await repo.list(clinic_id=clinic, page=1, page_size=1)
    assert total == 2
    assert len(items) == 1

    items, total = await repo.list(clinic_id=clinic, page=2, page_size=1)
    assert total == 2
    assert len(items) == 1

    # Filtro por estado (ambos PAID en este punto)
    items, total = await repo.list(clinic_id=clinic, status=PaymentStatus.PAID)
    assert total == 2

    # Filtro por cita
    items, total = await repo.list(clinic_id=clinic, appointment_id=appt)
    assert total == 2

    # Filtro por periodo: solo el mas antiguo entra en el rango pasado
    from_start = now - timedelta(days=40)
    to_start = now - timedelta(days=20)
    items, total = await repo.list(
        clinic_id=clinic, from_date=from_start, to_date=to_start
    )
    assert total == 1

    # Otro tenant no ve nada
    items, total = await repo.list(clinic_id=424242)
    assert total == 0

    # Cancelar uno y filtrar por estado CANCELLED
    cancelled = await repo.cancel(created2.id, clinic)
    assert cancelled is not None
    assert cancelled.status == PaymentStatus.CANCELLED
    assert cancelled.cancelled_at is not None

    items, total = await repo.list(clinic_id=clinic, status=PaymentStatus.CANCELLED)
    assert total == 1


@pytest.mark.asyncio
async def test_cancel_requires_tenant_and_returns_payment(db_session):
    appt, svc, clinic = _seed_tenant(db_session, "gamma")
    repo = get_payment_repo(db_session)
    created = await repo.create(_payment(appt, svc, clinic, method=PaymentMethod.CARD))

    result = await repo.cancel(created.id, clinic)
    assert result is not None
    assert result.status == PaymentStatus.CANCELLED

    # Tenant equivocado devuelve None (aislamiento)
    assert await repo.cancel(created.id, 555555) is None


@pytest.mark.asyncio
async def test_cancel_nonexistent_returns_none(db_session):
    _seed_tenant(db_session, "delta")
    repo = get_payment_repo(db_session)
    assert await repo.cancel(123123, 1) is None
    assert await repo.get_by_id(424242, 1) is None
