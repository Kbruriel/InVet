"""Entidades de dominio para reseñas y respuestas clinicas (BE-012)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewResponse(BaseModel):
    """Respuesta clínica única de una reseña."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    review_id: int = Field(..., gt=0)
    branch_id: int = Field(..., gt=0)
    user_id: int | None = None
    body: str = Field(..., max_length=2048)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Review(BaseModel):
    """Reseña de una cita completada (una por cita)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    appointment_id: int = Field(..., gt=0)
    branch_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    user_id: int | None = None
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=2048)
    response: ReviewResponse | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ReviewCreate(BaseModel):
    """Datos de entrada para crear una reseña."""

    appointment_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=2048)
    user_id: int | None = None


class ReviewRespond(BaseModel):
    """Datos de entrada para responder una reseña."""

    body: str = Field(..., min_length=1, max_length=2048)
    user_id: int | None = None
