"""ORM models registered for SQLAlchemy metadata."""

from app.infrastructure.database.models.availability_summary import AvailabilitySummary
from app.infrastructure.database.models.branch import Branch
from app.infrastructure.database.models.branch_schedule import BranchSchedule
from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.owner import Owner
from app.infrastructure.database.models.pet import Pet
from app.infrastructure.database.models.rating_summary import RatingSummary
from app.infrastructure.database.models.service import Service
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.veterinarian import Veterinarian

__all__ = [
    "AvailabilitySummary",
    "Branch",
    "BranchSchedule",
    "Clinic",
    "Owner",
    "Pet",
    "RatingSummary",
    "Service",
    "User",
    "Veterinarian",
]
