"""Router principal para la API v1."""

from fastapi import APIRouter

from app.api.v1.auth_router import router as auth_router
from app.api.v1.routers.branch_profile import router as branch_router
from app.api.v1.routers.clinic_admin import router as clinic_admin_router
from app.api.v1.routers.clinic_search import router as clinic_search_router
from app.api.v1.routers.internal_users import router as internal_users_router
from app.api.v1.routers.owners import router as owners_router
from app.api.v1.routers.pets import owner_pets_router, pet_router
from app.api.v1.routers.public_branches import router as public_branches_router
from app.api.v1.routers.public_clinics import router as public_clinics_router
from app.api.v1.routers.public_services import router as public_services_router
from app.api.v1.routers.services import router as services_router
from app.api.v1.routers.veterinarians import router as veterinarians_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(branch_router)
router.include_router(clinic_admin_router)
router.include_router(clinic_search_router)
router.include_router(public_clinics_router)
router.include_router(public_branches_router)
router.include_router(public_services_router)
router.include_router(services_router)
router.include_router(veterinarians_router)
router.include_router(internal_users_router)
router.include_router(owners_router)
router.include_router(owner_pets_router)
router.include_router(pet_router)


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Bienvenido a la API InVet v1"}
