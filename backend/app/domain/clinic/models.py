"""
Domain models for clinics.
This module defines the core entities and value objects for clinic management.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Clinic:
    """
    Domain model for a clinic entity.
    This represents the core business entity for clinic information.
    """

    id: Optional[int] = None
    name: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    postal_code: str = ""
    country: str = ""
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Initialize the datetime fields if not provided.
        """
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
