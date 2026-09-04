from typing import Generic, TypeVar

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Paginated wrapper (reutilizable en cualquier endpoint)
# ---------------------------------------------------------------------------

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int


# ---------------------------------------------------------------------------
# T01 – DTOs de reportes (BE-015)
# Campo por campo alineado con los modelos ORM de cada tabla.
# ---------------------------------------------------------------------------


class AppointmentSummaryDto(BaseModel):
    id: int
    clinic_id: int
    pet_name: str | None = None
    owner_name: str | None = None
    veterinarian_name: str | None = None
    appointment_type: str
    status: str
    scheduled_start: str  # ISO-8601 string for JSON serialisation
    scheduled_end: str


class ServiceSummaryDto(BaseModel):
    id: int
    clinic_id: int
    name: str
    description: str | None = None
    price: float  # converted from cents/int to $
    duration_minutes: int
    is_active: bool


class PetCountDto(BaseModel):
    clinic_id: int
    active_count: int


class ConsultationSummaryDto(BaseModel):
    id: int
    clinic_id: int
    pet_name: str | None = None
    veterinarian_name: str | None = None
    diagnosis: str | None = None
    history: str | None = None
    recommendations: str | None = None


class RatingSummaryDto(BaseModel):
    veterinarian_id: int | None = None
    average_rating: float
    total_reviews: int


class PaymentSummaryDto(BaseModel):
    id: int
    clinic_id: int
    appointment_id: int | None = None
    service_id: int | None = None
    amount: float  # converted from cents/int to $
    payment_method: str
    status: str
    paid_at: str  # ISO-8601 string
