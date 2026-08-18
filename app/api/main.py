# API entry point for the application.
# It imports the v1 router defined in the backend and mounts it.

from fastapi import FastAPI

# Import the router that aggregates all v1 endpoints.
from app.api.v1.router import router as api_v1_router

# Create the FastAPI application.
app = FastAPI(title="InVet API v1")

# Include the v1 router under the /v1 path.
app.include_router(api_v1_router, prefix="/v1")

# Expose the app as a module attribute for testing.
__all__ = ["app"]
