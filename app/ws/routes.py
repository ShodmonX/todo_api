"""
WebSocket endpoints for real-time notifications.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ws.manager import manager
from app.config import settings
from app.crud import get_user_by_email
from app.api.v1.deps import check_task_access


router = APIRouter()


async def _authenticate_websocket(websocket: WebSocket, token: str, session: AsyncSession):
    """
    Authenticate a WebSocket connection.
    
    Returns user if valid, None if invalid (connection already closed).
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
        email = payload.get("sub")
        if email is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return None
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None
    
    # Fetch user from database
    try:
        user = await get_user_by_email(session, email)
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return None
        return user
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Auth error")
        return None


@router.websocket("/ws/notifications")
async def ws_notifications(
    websocket: WebSocket,
    token: str = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for global real-time notifications.
    
    Query params:
    - token: JWT token for authentication
    """
    # Authenticate first
    user = await _authenticate_websocket(websocket, token, session)
    if user is None:
        return
    
    # Now accept the connection
    await manager.connect_global(websocket, user.id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "Connected to notifications"},
        })
        
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect_global(websocket, user.id)


@router.websocket("/ws/tasks/{task_id}")
async def ws_task(
    websocket: WebSocket,
    task_id: int,
    token: str = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for per-task real-time notifications.
    
    Path params:
    - task_id: The task ID to subscribe to
    
    Query params:
    - token: JWT token for authentication
    """
    # Authenticate first
    user = await _authenticate_websocket(websocket, token, session)
    if user is None:
        return
    
    # Verify user has access to this task
    try:
        await check_task_access(task_id, user, session)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Access denied")
        return
    
    # Now accept the connection
    await manager.connect_task(websocket, user.id, task_id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "data": {"message": f"Connected to task {task_id}"},
        })
        
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect_task(websocket, user.id, task_id)


@router.websocket("/ws/reminders")
async def ws_reminders(
    websocket: WebSocket,
    token: str = Query(None),
    session: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for reminder notifications.
    
    Query params:
    - token: JWT token for authentication
    """
    # Authenticate first
    user = await _authenticate_websocket(websocket, token, session)
    if user is None:
        return
    
    # Now accept the connection
    await manager.connect_reminders(websocket, user.id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "data": {"message": "Connected to reminders"},
        })
        
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect_reminders(websocket, user.id)
