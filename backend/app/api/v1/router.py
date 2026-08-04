"""Router principal para la API v1."""
from fastapi import APIRouter
from app.api.v1.routers.branch_profile import router as branch_router

router = APIRouter()
router.include_router(branch_router)


@router.get("/")
async def root():
    return {"message": "Bienvenido a la API InVet v1"}
