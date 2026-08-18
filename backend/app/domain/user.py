"""Re-export UserRole for backend tests."""

from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario disponibles"""

    OWNER = "owner"
    ADMIN = "admin"
    VETERINARIAN = "veterinarian"
    CLIENT = "client"
    STAFF = "staff"
