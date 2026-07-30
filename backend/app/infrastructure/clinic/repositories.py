"""
Repository implementation for clinic entities.
This module contains the data access layer for clinic operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.clinic.models import Clinic
from app.infrastructure.clinic.models import Clinic as ClinicDB


class ClinicRepository:
    """
    Repository class for clinic data access operations.
    This class implements the data access logic for clinics.
    """

    def __init__(self, db: Session):
        """
        Initialize the ClinicRepository with a database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, clinic_data: dict) -> Clinic:
        """
        Create a new clinic in the database.

        Args:
            clinic_data: Dictionary containing clinic information

        Returns:
            Created Clinic object
        """
        # Create database model instance
        db_clinic = ClinicDB(**clinic_data)
        self.db.add(db_clinic)
        self.db.commit()
        self.db.refresh(db_clinic)

        # Return domain model
        return self._db_to_domain(db_clinic)

    def get_by_id(self, clinic_id: int) -> Optional[Clinic]:
        """
        Retrieve a clinic by its ID from the database.

        Args:
            clinic_id: The ID of the clinic to retrieve

        Returns:
            Clinic object if found, None otherwise
        """
        db_clinic = self.db.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
        return self._db_to_domain(db_clinic) if db_clinic else None

    def get_all(self) -> List[Clinic]:
        """
        Retrieve all clinics from the database.

        Returns:
            List of Clinic objects
        """
        db_clinics = self.db.query(ClinicDB).all()
        return [self._db_to_domain(db_clinic) for db_clinic in db_clinics]

    def update(self, clinic_id: int, clinic_data: dict) -> Optional[Clinic]:
        """
        Update an existing clinic in the database.

        Args:
            clinic_id: The ID of the clinic to update
            clinic_data: Dictionary containing updated clinic information

        Returns:
            Updated Clinic object if found, None otherwise
        """
        db_clinic = self.db.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
        if not db_clinic:
            return None

        # Update fields
        for key, value in clinic_data.items():
            setattr(db_clinic, key, value)

        self.db.commit()
        self.db.refresh(db_clinic)

        return self._db_to_domain(db_clinic)

    def delete(self, clinic_id: int) -> bool:
        """
        Delete a clinic from the database.

        Args:
            clinic_id: The ID of the clinic to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        db_clinic = self.db.query(ClinicDB).filter(ClinicDB.id == clinic_id).first()
        if not db_clinic:
            return False

        self.db.delete(db_clinic)
        self.db.commit()
        return True

    def _db_to_domain(self, db_clinic: ClinicDB) -> Clinic:
        """
        Convert a database model to a domain model.

        Args:
            db_clinic: Database clinic model instance

        Returns:
            Domain clinic model instance
        """
        return Clinic(
            id=db_clinic.id,
            name=db_clinic.name,
            address=db_clinic.address,
            city=db_clinic.city,
            state=db_clinic.state,
            postal_code=db_clinic.postal_code,
            country=db_clinic.country,
            phone=db_clinic.phone,
            email=db_clinic.email,
            created_at=db_clinic.created_at,
            updated_at=db_clinic.updated_at,
        )
