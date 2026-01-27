from fastapi import FastAPI

from .config import settings
from .api import router
from .api.system import router as system_router
from .ws import ws_router

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Include system/operational endpoints (root level)
app.include_router(system_router)

# Include API routes
app.include_router(router)

# Include WebSocket routes
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"status": "ok"}