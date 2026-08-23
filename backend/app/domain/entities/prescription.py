"""Entidades de dominio para prescripciones (BE-010)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PrescriptionItemInput(BaseModel):
    """Medicamento informativo (entrada)."""

    name: str = Field(..., min_length=1, max_length=200)
    dosage: str | None = Field(None, max_length=200)
    frequency: str | None = Field(None, max_length=200)
    duration: str | None = Field(None, max_length=200)


class PrescriptionTreatmentInput(BaseModel):
    """Tratamiento informativo (entrada)."""

    name: str = Field(..., min_length=1, max_length=300)
    instructions: str = Field(default="", max_length=2000)


class PrescriptionReminderInput(BaseModel):
    """Recordatorio interno (entrada)."""

    title: str = Field(..., min_length=1, max_length=300)
    due_at: datetime | None = None
    note: str | None = Field(None, max_length=1000)


class PrescriptionItem(BaseModel):
    """Medicamento informativo (salida, con ID)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = Field(..., min_length=1, max_length=200)
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None


class PrescriptionTreatment(BaseModel):
    """Tratamiento informativo (salida, con ID)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str = Field(..., min_length=1, max_length=300)
    instructions: str = Field(default="", max_length=2000)


class PrescriptionReminder(BaseModel):
    """Recordatorio interno (salida, con ID)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str = Field(..., min_length=1, max_length=300)
    due_at: datetime | None = None
    note: str | None = None


class Prescription(BaseModel):
    """Receta veterinaria (salida completa, con items, tratamientos, recordatorios)."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    consultation_id: int = Field(..., gt=0)
    pet_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    branch_id: int | None = None
    veterinarian_id: int | None = None
    diagnosis: str = Field(..., min_length=1, max_length=2000)
    treatment_notes: str = Field(default="", max_length=3000)
    created_by: int | None = None
    items: list[PrescriptionItem] = []
    treatments: list[PrescriptionTreatment] = []
    reminders: list[PrescriptionReminder] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PrescriptionCreate(BaseModel):
    """Datos de entrada para crear una receta (caso de uso)."""

    consultation_id: int = Field(..., gt=0)
    pet_id: int = Field(..., gt=0)
    clinic_id: int = Field(..., gt=0)
    branch_id: int | None = None
    veterinarian_id: int | None = None
    diagnosis: str = Field(..., min_length=1, max_length=2000)
    treatment_notes: str = Field(default="", max_length=3000)
    items: list[PrescriptionItemInput] = []
    treatments: list[PrescriptionTreatmentInput] = []
    reminders: list[PrescriptionReminderInput] = []
    created_by: int | None = None
