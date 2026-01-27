"""
WebSocket authentication utilities.
"""

from fastapi import WebSocket, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.crud import get_user_by_id
from app.database import get_db


async def get_current_user_ws(websocket: WebSocket, token: str, session: AsyncSession):
    """
    Authenticate a WebSocket connection using JWT token.
    
    Args:
        websocket: The WebSocket connection
        token: JWT token from query param
        session: Database session
    
    Returns:
        User object if valid
    
    Raises:
        WebSocketException: If authentication fails
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No token provided")
        return None
    
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return None
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None
    
    # Fetch user from database
    try:
        user = await get_user_by_id(session, user_id)
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return None
        return user
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Auth error")
        return None
