"""Routers para la API v1."""
from fastapi import APIRouter

from app.api.clinic_router import branch_router
from app.api.clinic_router import router as clinic_router
from app.api.v1.internal_user_router import router as internal_user_router
from app.api.v1.owner_router import router as owner_router
from app.api.v1.pet_router import router as pet_router
from app.api.v1.service_router import router as service_router
from app.api.v1.veterinarian_router import router as veterinarian_router
from app.api.v1.appointment_router import router as appointment_router

router = APIRouter()


@router.get("/")
async def api_v1_root():
    return {"message": "Bienvenido a la API InVet v1"}


router.include_router(clinic_router)
router.include_router(branch_router)
router.include_router(service_router)
router.include_router(veterinarian_router)
router.include_router(internal_user_router)
router.include_router(owner_router)
router.include_router(pet_router)
router.include_router(appointment_router)
