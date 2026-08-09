"""Pruebas unitarias para casos de uso CRUD de clinica (BE-005)."""

import pytest

from app.application.use_cases.clinic_admin import (
    ActivateClinicUseCase,
    CreateClinicUseCase,
    DeactivateClinicUseCase,
    ListClinicsUseCase,
    UpdateClinicUseCase,
)
from app.domain.entities.clinic import Clinic


class MockClinicRepository:
    """Repositorio mock para pruebas unitarias."""

    def __init__(self) -> None:
        self._clinics: dict[int, Clinic] = {}
        self._next_id = 1

    async def search_clinics(self, **kwargs):
        return []

    async def get_clinic_count(self, **kwargs):
        return 0

    async def get_clinic_by_id(self, clinic_id: int):
        return self._clinics.get(clinic_id)

    async def create_clinic(self, clinic: Clinic) -> Clinic:
        id_ = self._next_id
        self._next_id += 1
        clinic.id = id_
        self._clinics[id_] = clinic
        return clinic

    async def update_clinic(self, clinic_id: int, data: dict):
        if clinic_id not in self._clinics:
            return None
        for key, value in data.items():
            if hasattr(self._clinics[clinic_id], key) and value is not None:
                setattr(self._clinics[clinic_id], key, value)
        return self._clinics[clinic_id]

    async def deactivate_clinic(self, clinic_id: int):
        if clinic_id not in self._clinics:
            return None
        self._clinics[clinic_id].is_active = False
        return self._clinics[clinic_id]

    async def activate_clinic(self, clinic_id: int):
        if clinic_id not in self._clinics:
            return None
        self._clinics[clinic_id].is_active = True
        return self._clinics[clinic_id]

    async def list_clinics_by_tenant(
        self, tenant_id: int, page: int = 1, size: int = 20
    ):
        items = list(self._clinics.values())
        total = len(items)
        offset = (page - 1) * size
        return (items[offset : offset + size], total)


def _make_clinic(**overrides):
    """Helper para crear Clinic con valores por defecto."""
    base = {
        "id": 0,
        "name": "Clinica Test",
        "address": "Calle 123",
        "city": "Ciudad",
        "state": "Estado",
        "country": "Mexico",
        "postal_code": "12345",
        "is_active": True,
    }
    base.update(overrides)
    return Clinic(**base)


def _make_clinic_data(**overrides):
    """Helper para crear datos de clinica con valores por defecto."""
    base = {
        "name": "Clinica Test",
        "address": "Calle 123",
        "city": "Ciudad",
        "state": "Estado",
        "country": "Mexico",
        "postal_code": "12345",
    }
    base.update(overrides)
    return base


class TestCreateClinicUseCase:
    """Pruebas para CreateClinicUseCase."""

    @pytest.mark.asyncio
    async def test_creates_clinic_with_valid_data(self) -> None:
        repo = MockClinicRepository()
        use_case = CreateClinicUseCase(repo)
        data = {**_make_clinic_data(), "phone": "555-1234", "email": "test@clinic.com"}
        clinic = await use_case.execute(data)
        assert clinic.id is not None
        assert isinstance(clinic, Clinic)
        assert clinic.name == "Clinica Test"
        assert clinic.is_active is True

    @pytest.mark.asyncio
    async def test_raises_on_missing_required_field(self) -> None:
        repo = MockClinicRepository()
        use_case = CreateClinicUseCase(repo)
        data = {"address": "Calle 123", "city": "Ciudad"}
        with pytest.raises(ValueError, match="El campo 'name' es obligatorio"):
            await use_case.execute(data)


class TestUpdateClinicUseCase:
    """Pruebas para UpdateClinicUseCase."""

    @pytest.mark.asyncio
    async def test_updates_existing_clinic(self) -> None:
        repo = MockClinicRepository()
        create_uc = CreateClinicUseCase(repo)
        clinic = await create_uc.execute(_make_clinic_data())

        update_uc = UpdateClinicUseCase(repo)
        updated = await update_uc.execute(clinic.id, {"name": "Clinica Actualizada"})
        assert updated is not None
        assert isinstance(updated, Clinic)
        assert updated.name == "Clinica Actualizada"

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_clinic(self) -> None:
        repo = MockClinicRepository()
        use_case = UpdateClinicUseCase(repo)
        result = await use_case.execute(999, {"name": "No existe"})
        assert result is None

    @pytest.mark.asyncio
    async def test_raises_on_no_valid_fields(self) -> None:
        repo = MockClinicRepository()
        use_case = UpdateClinicUseCase(repo)
        with pytest.raises(ValueError, match="campos.*actualizar"):
            await use_case.execute(1, {"invalid_field": "value"})


class TestDeactivateClinicUseCase:
    """Pruebas para DeactivateClinicUseCase."""

    @pytest.mark.asyncio
    async def test_deactivates_clinic(self) -> None:
        repo = MockClinicRepository()
        create_uc = CreateClinicUseCase(repo)
        clinic = await create_uc.execute(_make_clinic_data())

        deactivate_uc = DeactivateClinicUseCase(repo)
        result = await deactivate_uc.execute(clinic.id)
        assert result is not None
        assert isinstance(result, Clinic)
        assert result.is_active is False

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_clinic(self) -> None:
        repo = MockClinicRepository()
        use_case = DeactivateClinicUseCase(repo)
        result = await use_case.execute(999)
        assert result is None


class TestActivateClinicUseCase:
    """Pruebas para ActivateClinicUseCase."""

    @pytest.mark.asyncio
    async def test_activates_clinic(self) -> None:
        repo = MockClinicRepository()
        create_uc = CreateClinicUseCase(repo)
        clinic = await create_uc.execute(_make_clinic_data())

        deactivate_uc = DeactivateClinicUseCase(repo)
        await deactivate_uc.execute(clinic.id)

        activate_uc = ActivateClinicUseCase(repo)
        result = await activate_uc.execute(clinic.id)
        assert result is not None
        assert isinstance(result, Clinic)
        assert result.is_active is True


class TestListClinicsUseCase:
    """Pruebas para ListClinicsUseCase."""

    @pytest.mark.asyncio
    async def test_lists_clinics_with_pagination(self) -> None:
        repo = MockClinicRepository()
        for i in range(5):
            await CreateClinicUseCase(repo).execute(
                _make_clinic_data(name=f"Clinica {i}")
            )

        use_case = ListClinicsUseCase(repo)
        items, total = await use_case.execute(tenant_id=1, page=1, size=3)
        assert len(items) == 3
        assert total == 5
        for item in items:
            assert isinstance(item, Clinic)
