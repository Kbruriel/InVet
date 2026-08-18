# This package aggregates the API v1 routers expected by the test suite.
# The backend implementation uses a different package layout (backend\app\api\v1\routers).
# For compatibility with tests that import `app.api.v1.routers`, we provide minimal stubs
# that expose the router objects.  The actual router implementations live in the
# backend package, so these stubs simply import and re‑export the relevant routers.

# Each router is imported from the backend package where the real logic resides.
# The tests only need the router objects to exist; they do not call the endpoints
# directly.  Import errors are therefore avoided by providing these wrappers.

from backend.app.api.v1.routers.appointment_router import router as appointment_router
from backend.app.api.v1.routers.auth_router import router as auth_router
from backend.app.api.v1.routers.branch_profile import router as branch_router
from backend.app.api.v1.routers.clinic_admin import router as clinic_admin_router
from backend.app.api.v1.routers.clinic_search import router as clinic_search_router
from backend.app.api.v1.routers.internal_users import router as internal_users_router
from backend.app.api.v1.routers.owners import router as owners_router
# `public_branches`, `public_clinics`, `public_services`, `services`, and `veterinarians`
# are also re‑exported for completeness.
from backend.app.api.v1.routers.public_branches import router as public_branches_router
from backend.app.api.v1.routers.public_clinics import router as public_clinics_router
from backend.app.api.v1.routers.public_services import router as public_services_router
from backend.app.api.v1.routers.services import router as services_router
from backend.app.api.v1.routers.veterinarians import router as veterinarians_router

# Expose a list of router objects for easy inclusion in the main router.
__all__ = [
    "appointment_router",
    "auth_router",
    "branch_router",
    "clinic_admin_router",
    "clinic_search_router",
    "internal_users_router",
    "owners_router",
    "public_branches_router",
    "public_clinics_router",
    "public_services_router",
    "services_router",
    "veterinarians_router",
]# This package aggregates the API v1 routers expected by the test suite.
# The backend implementation uses a different package layout (backend\app\api\v1\routers).
# For compatibility with tests that import `app.api.v1.routers`, we provide minimal stubs
# that expose the router objects.  The actual router implementations live in the
# backend package, so these stubs simply import and re‑export the relevant routers.

# Each router is imported from the backend package where the real logic resides.
# The tests only need the router objects to exist; they do not call the endpoints
# directly.  Import errors are therefore avoided by providing these wrappers.

from backend.app.api.v1.routers.appointment_router import router as appointment_router
from backend.app.api.v1.routers.auth_router import router as auth_router
from backend.app.api.v1.routers.branch_profile import router as branch_router
from backend.app.api.v1.routers.clinic_admin import router as clinic_admin_router
from backend.app.api.v1.routers.clinic_search import router as clinic_search_router
from backend.app.api.v1.routers.internal_users import router as internal_users_router
from backend.app.api.v1.routers.owners import router as owners_router
# `public_branches`, `public_clinics`, `public_services`, `services`, and `veterinarians`
# are also re‑exported for completeness.
from backend.app.api.v1.routers.public_branches import router as public_branches_router
from backend.app.api.v1.routers.public_clinics import router as public_clinics_router
from backend.app.api.v1.routers.public_services import router as public_services_router
from backend.app.api.v1.routers.services import router as services_router
from backend.app.api.v1.routers.veterinarians import router as veterinarians_router

# Expose a list of router objects for easy inclusion in the main router.
__all__ = [
    "appointment_router",
    "auth_router",
    "branch_router",
    "clinic_admin_router",
    "clinic_search_router",
    "internal_users_router",
    "owners_router",
    "public_branches_router",
    "public_clinics_router",
    "public_services_router",
    "services_router",
    "veterinarians_router",
]
