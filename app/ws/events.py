"""
Event emission utilities for notifying WebSocket clients.
These are helper functions that HTTP endpoints can call to trigger broadcasts.
"""

import asyncio
from app.ws.manager import manager


async def notify_task_updated(task_id: int, payload: dict):
    """
    Broadcast a task update to all users subscribed to that task.
    
    Args:
        task_id: The task ID that was updated
        payload: Event payload (e.g., {"action": "updated", "task": {...}})
    """
    message = {
        "type": "task_updated",
        "data": payload
    }
    asyncio.create_task(manager.broadcast_task(task_id, message))


async def notify_task_comment_created(task_id: int, payload: dict):
    """Broadcast when a new comment is added to a task."""
    message = {
        "type": "comment_created",
        "data": payload
    }
    asyncio.create_task(manager.broadcast_task(task_id, message))


async def notify_task_subtask_created(task_id: int, payload: dict):
    """Broadcast when a new subtask is added to a task."""
    message = {
        "type": "subtask_created",
        "data": payload
    }
    asyncio.create_task(manager.broadcast_task(task_id, message))


async def notify_task_attachment_created(task_id: int, payload: dict):
    """Broadcast when a new attachment is added to a task."""
    message = {
        "type": "attachment_created",
        "data": payload
    }
    asyncio.create_task(manager.broadcast_task(task_id, message))


async def notify_reminder(payload: dict):
    """
    Broadcast a reminder event to all connected reminder channels.
    
    Args:
        payload: Event payload (e.g., {"action": "due", "reminder": {...}})
    """
    message = {
        "type": "reminder",
        "data": payload
    }
    asyncio.create_task(manager.broadcast_reminders(message))


async def notify_user_reminder(user_id: int, payload: dict):
    """
    Send a reminder notification to a specific user across all their connections.
    
    Args:
        user_id: The user to notify
        payload: Event payload
    """
    message = {
        "type": "reminder",
        "data": payload
    }
    asyncio.create_task(manager.send_to_user(user_id, message))


async def notify_global(payload: dict):
    """
    Broadcast a message to all global notification connections.
    
    Args:
        payload: Event payload
    """
    message = {
        "type": "notification",
        "data": payload
    }
    asyncio.create_task(manager.broadcast_global(message))
