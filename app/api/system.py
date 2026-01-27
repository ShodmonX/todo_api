"""
Operational endpoints for health checks, metrics, and version information.
"""

import time
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Any

from app.config import settings
from app.database import engine

router = APIRouter(tags=["System"])

# Track application start time for uptime calculation
_app_start_time = time.time()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns service health status including database connectivity.
    Returns 503 if database is unavailable.
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "todo-api"
    }
    
    try:
        # Check database connectivity with a lightweight query
        async with engine.connect() as conn:
            await conn.execute(__import__('sqlalchemy').text('SELECT 1'))
        
        health_status["database"] = "ok"
        
    except Exception as e:
        # Database is down
        health_status["status"] = "degraded"
        health_status["database"] = "unavailable"
        health_status["error"] = "Database connection failed"
        
        raise HTTPException(
            status_code=503,
            detail=health_status
        )
    
    # Add uptime
    uptime_seconds = int(time.time() - _app_start_time)
    health_status["uptime_seconds"] = uptime_seconds
    
    return health_status


@router.get("/version")
async def get_version() -> dict[str, Any]:
    """
    Get API version information.
    
    Returns service name, version, and other build information.
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "api_prefix": "/api/v1",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    """
    Get application metrics in JSON format.
    
    Returns basic operational metrics including request counts and system info.
    """
    uptime_seconds = int(time.time() - _app_start_time)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": uptime_seconds,
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "debug": settings.DEBUG,
        "database_status": await _get_db_status()
    }


async def _get_db_status() -> str:
    """Check database status."""
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__('sqlalchemy').text('SELECT 1'))
        return "healthy"
    except Exception:
        return "unhealthy"

