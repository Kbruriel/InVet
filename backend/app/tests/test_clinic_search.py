"""Tests para el caso de uso de búsqueda de clínicas."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.v1.schemas.clinic_search import ClinicSearchResponse
from app.application.use_cases.clinic_search import SearchClinicsUseCase
from app.domain.entities.clinic import Clinic
from app.infrastructure.database.models import Branch as BranchModel
from app.infrastructure.database.models import Clinic as ClinicModel
from app.infrastructure.database.models import Service as ServiceModel
from app.infrastructure.database.repositories.clinic_repository_impl import (
    ClinicRepositoryImpl,
)


@pytest.fixture
def mock_clinic_repo():
    """Mock del repositorio de clínicas."""
    repo = MagicMock()
    repo.search_clinics = AsyncMock(
        return_value=[
            Clinic(
                id=1,
                name="Clínica A",
                address="Calle Principal 123",
                city="Ciudad A",
                state="Estado A",
                country="País A",
                postal_code="12345",
                phone="1234567890",
                email="info@clinicaa.com",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        ]
    )
    repo.get_clinic_count = AsyncMock(return_value=1)
    return repo


@pytest.fixture
def search_use_case(mock_clinic_repo):
    """Caso de uso de búsqueda de clínicas."""
    return SearchClinicsUseCase(mock_clinic_repo)


class TestSearchClinicsUseCase:
    """Tests del caso de uso de búsqueda de clínicas."""

    @pytest.mark.asyncio
    async def test_execute_with_location_filter(
        self, search_use_case, mock_clinic_repo
    ):
        """Test búsqueda con filtro por ubicación."""
        # Act
        result = await search_use_case.execute(location="Ciudad A", page=1, size=10)

        # Assert
        assert isinstance(result, ClinicSearchResponse)
        assert len(result.data) == 1
        assert result.pagination["page"] == 1
        assert result.pagination["size"] == 10
        assert result.pagination["total"] == 1
        mock_clinic_repo.search_clinics.assert_called_once_with(
            location="Ciudad A", service_type=None, page=1, size=10
        )

    @pytest.mark.asyncio
    async def test_execute_with_page_size_validation(self, search_use_case):
        """Test validación de tamaño de página."""
        # Act & Assert
        with pytest.raises(
            ValueError, match="El tamaño de página debe estar entre 1 y 100"
        ):
            await search_use_case.execute(page=1, size=150)

    @pytest.mark.asyncio
    async def test_execute_with_no_filters(self, search_use_case, mock_clinic_repo):
        """Test búsqueda sin filtros."""
        # Act
        result = await search_use_case.execute(page=1, size=5)

        # Assert
        assert isinstance(result, ClinicSearchResponse)
        assert len(result.data) == 1
        mock_clinic_repo.search_clinics.assert_called_once_with(
            location=None, service_type=None, page=1, size=5
        )

    @pytest.mark.asyncio
    async def test_execute_with_service_type_filter(
        self, search_use_case, mock_clinic_repo
    ):
        """Test búsqueda con filtro por tipo de servicio."""
        # Act
        result = await search_use_case.execute(
            location="Ciudad A",
            service_type="estetica",
            page=1,
            size=10,
        )

        # Assert
        assert isinstance(result, ClinicSearchResponse)
        mock_clinic_repo.search_clinics.assert_called_once_with(
            location="Ciudad A", service_type="estetica", page=1, size=10
        )


class TestClinicRepositoryImpl:
    """Tests del repositorio de clínicas."""

    def test_to_domain_accepts_legacy_rows_without_timestamps(self):
        """Convierte registros antiguos aunque no tengan timestamps."""
        repository = ClinicRepositoryImpl(MagicMock())
        legacy_clinic = ClinicModel(
            id=2,
            name="Clínica Legacy",
            address="Calle Antigua 456",
            city="Ciudad Legacy",
            state="Estado Legacy",
            country="País Legacy",
            postal_code="67890",
            phone=None,
            email=None,
            is_active=True,
            created_at=None,
            updated_at=None,
        )

        result = repository._to_domain(legacy_clinic)

        assert result.name == "Clínica Legacy"
        assert result.created_at is not None
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_search_clinics_filters_by_service_type(self, db_session):
        """Filtra clínicas por servicios asociados con coincidencia tolerante a acentos."""
        clinic_match = ClinicModel(
            name="Clínica Estética",
            address="Calle Uno 123",
            city="Ciudad A",
            state="Estado A",
            country="País A",
            postal_code="12345",
            phone=None,
            email=None,
            is_active=True,
        )
        clinic_other = ClinicModel(
            name="Clínica General",
            address="Calle Dos 456",
            city="Ciudad B",
            state="Estado B",
            country="País B",
            postal_code="67890",
            phone=None,
            email=None,
            is_active=True,
        )
        db_session.add_all([clinic_match, clinic_other])
        db_session.flush()
        branch_match = BranchModel(
            clinic_id=clinic_match.id,
            name="Sucursal Estética",
            description="Sucursal para estética",
            address="Calle Uno 123",
            city="Ciudad A",
            state="Estado A",
            country="País A",
            postal_code="12345",
        )
        branch_other = BranchModel(
            clinic_id=clinic_other.id,
            name="Sucursal General",
            description="Sucursal general",
            address="Calle Dos 456",
            city="Ciudad B",
            state="Estado B",
            country="País B",
            postal_code="67890",
        )
        db_session.add_all([branch_match, branch_other])
        db_session.flush()
        db_session.add_all(
            [
                ServiceModel(
                    branch_id=branch_match.id,
                    clinic_id=clinic_match.id,
                    name="Estética canina",
                    description="Baño y corte",
                    price=5000,
                    duration_minutes=45,
                    is_active=True,
                ),
                ServiceModel(
                    branch_id=branch_other.id,
                    clinic_id=clinic_other.id,
                    name="Consulta general",
                    description="Medicina preventiva",
                    price=4000,
                    duration_minutes=30,
                    is_active=True,
                ),
            ]
        )
        db_session.commit()

        repository = ClinicRepositoryImpl(db_session)

        matched_clinics = await repository.search_clinics(
            service_type="estetica",
            page=1,
            size=10,
        )
        matched_count = await repository.get_clinic_count(service_type="estetica")

        assert [clinic.id for clinic in matched_clinics] == [clinic_match.id]
        assert matched_count == 1
