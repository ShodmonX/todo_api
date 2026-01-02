from fastapi import FastAPI

from .config import settings
from .api import router

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "ok"}