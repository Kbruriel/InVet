"""Schemas Pydantic para reseñas y respuestas clínicas (BE-012)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    """Schema para crear una reseña de una cita COMPLETED.

    - ``appointment_id`` debe referir a una cita COMPLETED del tenant del usuario.
    - ``rating`` es una estrella entera de 1 a 5.
    - ``comment`` es opcional y máximo 2048 caracteres.
    """

    appointment_id: int = Field(..., gt=0, description="ID de la cita calificada")
    rating: int = Field(..., ge=1, le=5, description="Puntuación de 1 a 5 estrellas")
    comment: str | None = Field(
        None, max_length=2048, description="Comentario opcional (máximo 2048 caracteres)"
    )


class ReviewResponseRead(BaseModel):
    """Respuesta clínica única de una reseña."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: int
    branch_id: int
    user_id: int | None = None
    body: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReviewRead(BaseModel):
    """Respuesta para una reseña con su respuesta clínica (si existe)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    branch_id: int
    clinic_id: int
    user_id: int | None = None
    rating: int
    comment: str | None = None
    response: ReviewResponseRead | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReviewRespond(BaseModel):
    """Schema para responder una reseña (respuesta única por reseña)."""

    body: str = Field(..., min_length=1, max_length=2048, description="Cuerpo de la respuesta")


class ReviewListMeta(BaseModel):
    """Metadatos de paginación de listados de reseñas."""

    page: int
    page_size: int
    total: int
    pages: int


class ReviewList(BaseModel):
    """Listado paginado de reseñas."""

    items: list[ReviewRead]
    meta: ReviewListMeta
