from fastapi import FastAPI
from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router

app = FastAPI(
    title="InVet API",
    version="1.0.0",
    description="API para la plataforma InVet"
)

# Incluir los routers
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
async def root():
    return {"message": "Welcome to InVet API"}
