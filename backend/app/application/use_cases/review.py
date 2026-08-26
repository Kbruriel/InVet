"""Casos de uso para reseñas y respuestas clinicas (BE-012).

Encapsula las reglas de negocio del dominio:
- Una cita COMPLETED solo puede recibir una reseña (409 si ya existe).
- El propietario debe ser el titular de la cita (403/404/422).
- Solo rol clinico de la misma sucursal puede responder (403).
- Una reseña solo puede recibir una respuesta (409 si ya existe).
- Tras crear una reseña se recalcula RatingSummary para la sucursal.
"""

from __future__ import annotations

from typing import Any

from app.domain.entities.appointment import AppointmentStatus
from app.domain.entities.review import (
    Review,
    ReviewCreate,
    ReviewRespond,
    ReviewResponse,
)
from app.domain.repositories.appointment_repository import AppointmentRepository
from app.domain.repositories.branch_repository import RatingSummaryRepository
from app.data.review_repo import ReviewRepository


class ReviewError(Exception):
    """Error base de las operaciones de reseñas."""

    status_code = 400
    message = "Operacion de reseña invalida"


class ReviewNotCompletedError(ReviewError):
    """La cita no se encontro o no esta en estado COMPLETED."""

    status_code = 422
    message = "La cita no existe o no esta COMPLETED"


class ReviewNotAuthorizedError(ReviewError):
    """El usuario no es el propietario de la cita o no esta en el tenant."""

    status_code = 403
    message = "No autorizado a calificar esta cita"


class ReviewDuplicateError(ReviewError):
    """La cita ya fue calificada por este propietario."""

    status_code = 409
    message = "La cita ya cuenta con una reseña"


class ReviewNotFoundError(ReviewError):
    """La reseña no existe en el tenant."""

    status_code = 404
    message = "Reseña no encontrada"


class ReviewRespondForbiddenError(ReviewError):
    """El usuario no tiene rol clinico de la sucursal."""

    status_code = 403
    message = "Solo el equipo clinico de la sucursal puede responder"


class ReviewRespondNotFoundError(ReviewError):
    """La reseña no existe para responder."""

    status_code = 404
    message = "Reseña no encontrada para responder"


class ReviewRespondDuplicateError(ReviewError):
    """La reseña ya cuenta con una respuesta clinica."""

    status_code = 409
    message = "La reseña ya cuenta con una respuesta"


class ReviewService:
    """Orquestacion de altas y respues de reseñas con recalculo de resumen."""

    def __init__(
        self,
        review_repo: ReviewRepository,
        appointment_repo: AppointmentRepository,
        rating_repo: RatingSummaryRepository,
    ) -> None:
        self.review_repo = review_repo
        self.appointment_repo = appointment_repo
        self.rating_repo = rating_repo

    async def create(
        self, payload: ReviewCreate, current_user: dict[str, Any]
    ) -> Review:
        """Validar contexto de la cita y persistir la reseña con resumen."""
        clinic_id = int(current_user.get("clinic_id") or 0)
        user_id = int(current_user.get("id") or 0)
        if clinic_id == 0:
            raise ReviewNotAuthorizedError()
        if user_id == 0:
            raise ReviewNotAuthorizedError()

        # Validar que la cita se encuentra COMPLETED y pertenece al tenant.
        appointment = await self._get_completed_appointment(
            appointment_id=payload.appointment_id,
            clinic_id=clinic_id,
        )
        # Aislamiento de tenant propietario: solo el owner de la cita puede calificar.
        owner_id = await self.review_repo.get_owner_id_by_user(user_id)
        if owner_id is None or int(getattr(appointment, "owner_id", 0)) != int(owner_id):
            raise ReviewNotAuthorizedError()

        if await self.review_repo.exists_by_appointment(payload.appointment_id):
            raise ReviewDuplicateError()

        review = Review(
            appointment_id=payload.appointment_id,
            branch_id=int(appointment.branch_id or 0),
            clinic_id=clinic_id,
            user_id=owner_id,
            rating=payload.rating,
            comment=payload.comment,
        )
        created = await self.review_repo.create(review)

        total, distribution = await self.review_repo.get_review_stats(
            created.branch_id
        )
        if total > 0:
            average = sum(
                rating * count for rating, count in distribution.items()
            ) / total
            await self.rating_repo.upsert_rating_summary(
                branch_id=created.branch_id,
                average_rating=round(average, 2),
                total_reviews=total,
                review_distribution={int(k): int(v) for k, v in distribution.items()},
            )
        return created

    async def respond(
        self,
        review_id: int,
        payload: ReviewRespond,
        current_user: dict[str, Any],
    ) -> Review:
        """Responder una reseña (una unica respuesta por reseña)."""
        clinic_id = int(current_user.get("clinic_id") or 0)
        user_id = int(current_user.get("id") or 0)
        role = str(current_user.get("role") or "")
        if clinic_id == 0:
            raise ReviewRespondForbiddenError()
        if role not in ("veterinarian", "internal", "admin", "staff", "clinic"):
            raise ReviewRespondForbiddenError()

        review = await self.review_repo.get_by_id(review_id, clinic_id)
        if review is None:
            raise ReviewRespondNotFoundError()
        if review.response is not None:
            raise ReviewRespondDuplicateError()

        internal_user_id = (
            await self.review_repo.get_internal_user_id_by_user(user_id) or user_id
        )
        created_response = await self.review_repo.create_response(
            ReviewResponse(
                review_id=review.id,
                branch_id=review.branch_id,
                user_id=internal_user_id,
                body=payload.body,
            )
        )
        if review.id is not None and review.response is None:
            review.response = created_response
        return review

    async def get(self, review_id: int, clinic_id: int) -> Review:
        """Obtener una reseña con aislamiento de tenant."""
        review = await self.review_repo.get_by_id(review_id, clinic_id)
        if review is None:
            raise ReviewNotFoundError()
        return review

    async def list_public(
        self,
        branch_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int]:
        return await self.review_repo.list_by_branch(
            branch_id=branch_id, page=page, page_size=page_size
        )

    async def list_clinical(
        self,
        clinic_id: int,
        branch_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Review], int]:
        return await self.review_repo.list_by_clinic(
            clinic_id=clinic_id,
            branch_id=branch_id,
            page=page,
            page_size=page_size,
        )

    async def _get_completed_appointment(
        self, appointment_id: int, clinic_id: int
    ) -> Any:
        appointment = await self.appointment_repo.get_by_id(
            appointment_id, clinic_id
        )
        if appointment is None:
            raise ReviewNotCompletedError()
        if appointment.status != AppointmentStatus.COMPLETED:
            raise ReviewNotCompletedError()
        return appointment
