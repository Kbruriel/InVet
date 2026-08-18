"""Configuración central de la aplicación."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "InVet"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "invet"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/invet"

    # SECRET_KEY must be injected via environment variable or .env file. No default allowed.
    SECRET_KEY: str = Field(
        "change-me-in-development",
        description="JWT secret key — required at runtime",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Execution environment: 'development', 'staging', 'production'
    ENVIRONMENT: str = "development"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
