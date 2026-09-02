"""ORM models registered for SQLAlchemy metadata."""

from app.infrastructure.database.models.appointment import Appointment
from app.infrastructure.database.models.assignment_model import (
    VeterinarianServiceAssignment,
)
from app.infrastructure.database.models.availability_summary import AvailabilitySummary
from app.infrastructure.database.models.base import Base
from app.infrastructure.database.models.branch import Branch
from app.infrastructure.database.models.branch_schedule import BranchSchedule
from app.infrastructure.database.models.clinic import Clinic
from app.infrastructure.database.models.consultation import Consultation
from app.infrastructure.database.models.internal_user_model import InternalUser
from app.infrastructure.database.models.notification import Notification
from app.infrastructure.database.models.owner import Owner
from app.infrastructure.database.models.payment import Payment
from app.infrastructure.database.models.pet import Pet
from app.infrastructure.database.models.prescription import (
    Prescription,
    PrescriptionItem,
    PrescriptionReminder,
    PrescriptionTreatment,
)
from app.infrastructure.database.models.rating_summary import RatingSummary
from app.infrastructure.database.models.review import Review, ReviewResponse
from app.infrastructure.database.models.service_model import Service
from app.infrastructure.database.models.session import Session
from app.infrastructure.database.models.support_ticket_model import (
    SupportTicket,
    TicketCategory,
    TicketStatus,
)
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.veterinarian_model import Veterinarian

__all__ = [
    "Appointment",
    "AvailabilitySummary",
    "Base",
    "Branch",
    "BranchSchedule",
    "Clinic",
    "Consultation",
    "InternalUser",
    "Notification",
    "Owner",
    "Payment",
    "Pet",
    "Prescription",
    "PrescriptionItem",
    "PrescriptionReminder",
    "PrescriptionTreatment",
    "RatingSummary",
    "Review",
    "ReviewResponse",
    "Service",
    "Session",
    "SupportTicket",
    "TicketCategory",
    "TicketStatus",
    "User",
    "Veterinarian",
    "VeterinarianServiceAssignment",
]
