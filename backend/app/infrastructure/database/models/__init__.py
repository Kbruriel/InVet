"""Modelos ORM para SQLAlchemy."""

from app.infrastructure.database.models.appointment import (  # noqa: F401
    Appointment,
    AppointmentSlot,
)
from app.infrastructure.database.models.clinic import Clinic  # noqa: F401
from app.infrastructure.database.models.internal_user import InternalUser  # noqa: F401
from app.infrastructure.database.models.owner import Owner  # noqa: F401
from app.infrastructure.database.models.pet import Pet  # noqa: F401
from app.infrastructure.database.models.service import Service  # noqa: F401
from app.infrastructure.database.models.user import User  # noqa: F401
from app.infrastructure.database.models.veterinarian import Veterinarian  # noqa: F401

# Importar para asegurar que todos los modelos estén registrados
from app.infrastructure.database.session import Base  # noqa: F401

__all__ = [
    "User",
    "Clinic",
    "Veterinarian",
    "Owner",
    "Pet",
    "Service",
    "InternalUser",
    "Appointment",
    "AppointmentSlot",
    "Base",
]
