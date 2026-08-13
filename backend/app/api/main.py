"""Punto de entrada principal de la aplicación FastAPI."""

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    # Security runtime validation: ensure SECRET_KEY is not the default in production
    try:
        env = settings.ENVIRONMENT.lower()
    except Exception:
        env = "development"

    if env in ("prod", "production"):
        if not settings.SECRET_KEY or settings.SECRET_KEY == "secret-key-for-dev":
            raise RuntimeError(
                "In production ENVIRONMENT, SECRET_KEY must be set and not use the default placeholder."
            )

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "InVet Backend API"}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
