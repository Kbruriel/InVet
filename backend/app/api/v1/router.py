"""Primary router for API v1."""
from fastapi import APIRouter

from app.api.clinic_router import branch_router
from app.api.clinic_router import router as clinic_router

router = APIRouter()


@router.get("/")
async def api_v1_root():
    return {"message": "Bienvenido a la API InVet v1"}


router.include_router(clinic_router)
router.include_router(branch_router)
