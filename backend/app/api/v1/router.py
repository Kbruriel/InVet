"""Router principal para la API v1."""

from fastapi import APIRouter

from app.api.v1.auth_router import router as auth_router
from app.api.v1.routers.branch_profile import router as branch_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(branch_router)


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Bienvenido a la API InVet v1"}
