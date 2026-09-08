from typing import Generic, TypeVar

from pydantic import BaseModel, Field

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


# ---------------------------------------------------------------------------
# T08–T13 – Response models agregados (BE-015)
#
# Estos modelos agregan sobre `PaginatedResponse` o sobre un DTO propio con
# campos de agregación. Antes vivían inline en `reports_router.py` (F1 de
# la review BE-015); ahora están aquí para que el contrato HTTP completo esté
# en una sola capa (schemas).
# ---------------------------------------------------------------------------


class RatingsReportResponse(BaseModel):
    by_veterinarian: list[RatingSummaryDto] = Field(
        description=(
            "Resumen de calificaciones por veterinario. Cada elemento incluye "
            "`veterinarian_id` (puede ser `None` si el modelo `RatingSummary` "
            "no expone la relación), `average_rating` y `total_reviews`."
        ),
    )
    clinic_avg: float = Field(
        description=(
            "Promedio de calificaciones de toda la clínica, **ponderado** por "
            "el número de reseñas de cada veterinario "
            "(`sum(avg_v * total_reviews_v) / sum(total_reviews_v)`; `0.0` si "
            "no hay reseñas). Ver BE-015 F2."
        ),
    )


class PaymentsReportResponse(BaseModel):
    items: list[PaymentSummaryDto] = Field(
        description="Listado paginado de pagos operativos de la clínica."
    )
    total: int = Field(description="Total de pagos encontrados (todas las páginas).")
    page: int = Field(description="Página actual (1-indexed).")
    size: int = Field(description="Elementos por página.")
    total_amount: float = Field(
        description=(
            "Suma de `amount` en la página actual (`round(sum(items.amount), 2)`); "
            "no es el total histórico de la clínica."
        ),
    )
