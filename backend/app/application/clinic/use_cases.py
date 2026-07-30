"""
Use cases for clinic management.
This module contains the business logic for clinic operations.
"""

from typing import List, Optional

from app.domain.clinic.models import Clinic
from app.infrastructure.clinic.repositories import ClinicRepository


class ClinicUseCase:
    """
    Use case class for clinic-related operations.
    This class encapsulates the business logic for clinic management.
    """

    def __init__(self, clinic_repository: ClinicRepository):
        """
        Initialize the ClinicUseCase with a repository instance.

        Args:
            clinic_repository: Instance of ClinicRepository
        """
        self.clinic_repository = clinic_repository

    def create_clinic(self, clinic_data: dict) -> Clinic:
        """
        Create a new clinic.

        Args:
            clinic_data: Dictionary containing clinic information

        Returns:
            Created Clinic object
        """
        return self.clinic_repository.create(clinic_data)

    def get_clinic_by_id(self, clinic_id: int) -> Optional[Clinic]:
        """
        Retrieve a clinic by its ID.

        Args:
            clinic_id: The ID of the clinic to retrieve

        Returns:
            Clinic object if found, None otherwise
        """
        return self.clinic_repository.get_by_id(clinic_id)

    def get_clinics(self) -> List[Clinic]:
        """
        Retrieve all clinics.

        Returns:
            List of all Clinic objects
        """
        return self.clinic_repository.get_all()

    def update_clinic(self, clinic_id: int, clinic_data: dict) -> Optional[Clinic]:
        """
        Update an existing clinic.

        Args:
            clinic_id: The ID of the clinic to update
            clinic_data: Dictionary containing updated clinic information

        Returns:
            Updated Clinic object if found, None otherwise
        """
        return self.clinic_repository.update(clinic_id, clinic_data)

    def delete_clinic(self, clinic_id: int) -> bool:
        """
        Delete a clinic.

        Args:
            clinic_id: The ID of the clinic to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        return self.clinic_repository.delete(clinic_id)
