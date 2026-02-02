from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api import router
from .api.system import router as system_router
from .ws import ws_router

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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