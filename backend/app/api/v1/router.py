"""Router principal para la API v1."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Bienvenido a la API InVet v1"}
