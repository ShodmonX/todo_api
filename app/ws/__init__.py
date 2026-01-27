"""
WebSocket module for real-time notifications.
"""

from .manager import manager
from .routes import router as ws_router


__all__ = [
    "manager",
    "ws_router"
]
