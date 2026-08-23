"""Modelos ORM de recetas veterinarias para BE-010."""

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.models.base import Base


class Prescription(Base):
    """Modelo de recetas veterinarias para la base de datos (BE-010)."""

    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(
        Integer, ForeignKey("consultations.id", ondelete="CASCADE"), nullable=False
    )
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False)
    clinic_id = Column(
        Integer, ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False
    )
    branch_id = Column(
        Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True
    )
    veterinarian_id = Column(
        Integer, ForeignKey("veterinarians.id", ondelete="SET NULL"), nullable=True
    )
    diagnosis = Column(Text, nullable=False)
    treatment_notes = Column(Text, nullable=False, default="")
    created_by = Column(
        Integer, ForeignKey("internal_users.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relaciones
    items = relationship(
        "PrescriptionItem",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )
    treatments = relationship(
        "PrescriptionTreatment",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )
    reminders = relationship(
        "PrescriptionReminder",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Prescription(id={self.id}, consultation_id={self.consultation_id})>"


class PrescriptionItem(Base):
    """Medicamento informativo de una receta (BE-010)."""

    __tablename__ = "prescription_items"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(
        Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(200), nullable=False)
    dosage = Column(String(200), nullable=True)
    frequency = Column(String(200), nullable=True)
    duration = Column(String(200), nullable=True)

    prescription = relationship("Prescription", back_populates="items")

    def __repr__(self) -> str:
        return f"<PrescriptionItem(id={self.id}, name={self.name!r})>"


class PrescriptionTreatment(Base):
    """Tratamiento informativo de una receta (BE-010)."""

    __tablename__ = "prescription_treatments"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(
        Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(300), nullable=False)
    instructions = Column(Text, nullable=False, default="")

    prescription = relationship("Prescription", back_populates="treatments")

    def __repr__(self) -> str:
        return f"<PrescriptionTreatment(id={self.id}, name={self.name!r})>"


class PrescriptionReminder(Base):
    """Recordatorio interno de una receta (BE-010)."""

    __tablename__ = "prescription_reminders"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(
        Integer, ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(300), nullable=False)
    due_at = Column(DateTime, nullable=True)
    note = Column(String(1000), nullable=True)

    prescription = relationship("Prescription", back_populates="reminders")

    def __repr__(self) -> str:
        return f"<PrescriptionReminder(id={self.id}, title={self.title!r})>"
