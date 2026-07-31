"""Repository interfaces for clinics, branches, services, schedules, and ratings."""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.clinic import Branch, Clinic, Schedule, Service


class ClinicRepository(ABC):
    """Repository interface for clinic administration."""

    @abstractmethod
    async def get_clinic_by_id(self, clinic_id: int) -> Optional[Clinic]:
        """Return a clinic by ID."""

    @abstractmethod
    async def list_active_clinics(
        self, skip: int = 0, limit: int = 100
    ) -> List[Clinic]:
        """Return active clinics with pagination."""

    @abstractmethod
    async def list_clinics(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Clinic]:
        """Return clinics with administration filters."""

    @abstractmethod
    async def count_clinics(
        self,
        user_id: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """Return the total clinic count for administration filters."""

    @abstractmethod
    async def create_clinic(self, data: dict) -> Clinic:
        """Create a clinic."""

    @abstractmethod
    async def update_clinic(self, clinic_id: int, data: dict) -> Optional[Clinic]:
        """Update a clinic."""

    @abstractmethod
    async def deactivate_clinic(self, clinic_id: int) -> bool:
        """Logically delete a clinic."""

    @abstractmethod
    async def is_clinic_accessible(
        self, clinic_id: int, user_id: Optional[int]
    ) -> bool:
        """Return whether a user can administer a clinic."""


class BranchRepository(ABC):
    """Repository interface for branch administration."""

    @abstractmethod
    async def get_branch_by_id(self, branch_id: int) -> Optional[Branch]:
        """Return a branch by ID."""

    @abstractmethod
    async def get_branch_by_clinic_and_id(
        self, clinic_id: int, branch_id: int
    ) -> Optional[Branch]:
        """Return a branch by clinic and branch ID."""

    @abstractmethod
    async def list_active_branches_by_clinic(
        self, clinic_id: int, skip: int = 0, limit: int = 100
    ) -> List[Branch]:
        """Return active branches for a clinic."""

    @abstractmethod
    async def list_branches(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        clinic_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Branch]:
        """Return branches with administration filters."""

    @abstractmethod
    async def count_branches(
        self,
        user_id: int,
        clinic_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> int:
        """Return the total branch count for administration filters."""

    @abstractmethod
    async def create_branch(self, data: dict) -> Branch:
        """Create a branch."""

    @abstractmethod
    async def update_branch(self, branch_id: int, data: dict) -> Optional[Branch]:
        """Update a branch."""

    @abstractmethod
    async def deactivate_branch(self, branch_id: int) -> bool:
        """Logically delete a branch."""

    @abstractmethod
    async def get_branch_schedule(self, branch_id: int) -> List[Schedule]:
        """Return public schedules for a branch."""

    @abstractmethod
    async def get_branch_services(self, branch_id: int) -> List[Service]:
        """Return services for a branch."""

    @abstractmethod
    async def get_branch_ratings_summary(self, branch_id: int) -> dict:
        """Return a rating summary for a branch."""

    @abstractmethod
    async def is_branch_accessible(
        self, branch_id: int, user_id: Optional[int] = None
    ) -> bool:
        """Return whether a user can access a branch."""


class ServiceRepository(ABC):
    """Repository interface for services."""

    @abstractmethod
    async def get_service_by_branch_and_id(
        self, branch_id: int, service_id: int
    ) -> Optional[Service]:
        """Return a service by branch and ID."""

    @abstractmethod
    async def list_active_services_by_branch(
        self, branch_id: int, skip: int = 0, limit: int = 100
    ) -> List[Service]:
        """Return active services for a branch."""


class ScheduleRepository(ABC):
    """Repository interface for schedules."""

    @abstractmethod
    async def list_schedule_by_branch(self, branch_id: int) -> List[Schedule]:
        """Return public schedules for a branch."""

    @abstractmethod
    async def list_branch_hours(self, branch_id: int) -> List[Schedule]:
        """Return administration schedules for a branch."""

    @abstractmethod
    async def get_schedule_by_id(
        self, branch_id: int, schedule_id: int
    ) -> Optional[Schedule]:
        """Return a schedule by branch and ID."""

    @abstractmethod
    async def create_schedule(self, branch_id: int, data: dict) -> Schedule:
        """Create branch hours."""

    @abstractmethod
    async def update_schedule(
        self, branch_id: int, schedule_id: int, data: dict
    ) -> Optional[Schedule]:
        """Update branch hours."""

    @abstractmethod
    async def delete_schedule(self, branch_id: int, schedule_id: int) -> bool:
        """Delete branch hours."""


class RatingRepository(ABC):
    """Repository interface for ratings."""

    @abstractmethod
    async def get_ratings_summary_by_branch(self, branch_id: int) -> dict:
        """Return a rating summary for a branch."""
