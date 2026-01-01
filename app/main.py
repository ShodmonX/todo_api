from fastapi import FastAPI

from .config import settings
from .api.v1 import router as v1_router

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.include_router(v1_router)

@app.get("/")
async def root():
    return {"status": "ok"}