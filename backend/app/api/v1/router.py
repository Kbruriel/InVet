"""Router principal para la API v1."""
from fastapi import APIRouter
from app.api.clinic_router import router as clinic_router

router = APIRouter()
router.include_router(clinic_router)
