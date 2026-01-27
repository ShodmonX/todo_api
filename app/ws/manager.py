"""
WebSocket connection manager for handling real-time notifications.
Manages connections for global notifications, per-task channels, and reminders.
"""

from fastapi import WebSocket
from typing import Dict, Set, Callable, Any
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self):
        # Global notifications: set of WebSockets
        self.global_connections: Set[tuple[WebSocket, int]] = set()  # (ws, user_id)
        
        # Per-task notifications: task_id -> set of (ws, user_id)
        self.task_connections: Dict[int, Set[tuple[WebSocket, int]]] = {}
        
        # Reminders: set of (ws, user_id)
        self.reminder_connections: Set[tuple[WebSocket, int]] = set()

    async def connect_global(self, websocket: WebSocket, user_id: int):
        """Add a connection to global notifications channel."""
        await websocket.accept()
        self.global_connections.add((websocket, user_id))

    async def connect_task(self, websocket: WebSocket, user_id: int, task_id: int):
        """Add a connection to a per-task notifications channel."""
        await websocket.accept()
        if task_id not in self.task_connections:
            self.task_connections[task_id] = set()
        self.task_connections[task_id].add((websocket, user_id))

    async def connect_reminders(self, websocket: WebSocket, user_id: int):
        """Add a connection to reminders channel."""
        await websocket.accept()
        self.reminder_connections.add((websocket, user_id))

    def disconnect_global(self, websocket: WebSocket, user_id: int):
        """Remove a connection from global notifications."""
        self.global_connections.discard((websocket, user_id))

    def disconnect_task(self, websocket: WebSocket, user_id: int, task_id: int):
        """Remove a connection from a per-task channel."""
        if task_id in self.task_connections:
            self.task_connections[task_id].discard((websocket, user_id))
            if not self.task_connections[task_id]:
                del self.task_connections[task_id]

    def disconnect_reminders(self, websocket: WebSocket, user_id: int):
        """Remove a connection from reminders channel."""
        self.reminder_connections.discard((websocket, user_id))

    async def broadcast_global(self, message: dict[str, Any]):
        """Broadcast a message to all global connections."""
        disconnected = set()
        for websocket, user_id in self.global_connections:
            try:
                await websocket.send_json(self._format_message(message))
            except Exception:
                disconnected.add((websocket, user_id))
        
        for conn in disconnected:
            self.global_connections.discard(conn)

    async def broadcast_task(self, task_id: int, message: dict[str, Any]):
        """Broadcast a message to all connections in a task channel."""
        if task_id not in self.task_connections:
            return

        disconnected = set()
        for websocket, user_id in self.task_connections[task_id]:
            try:
                await websocket.send_json(self._format_message(message))
            except Exception:
                disconnected.add((websocket, user_id))
        
        for conn in disconnected:
            self.task_connections[task_id].discard(conn)

    async def broadcast_reminders(self, message: dict[str, Any]):
        """Broadcast a message to all reminder channel connections."""
        disconnected = set()
        for websocket, user_id in self.reminder_connections:
            try:
                await websocket.send_json(self._format_message(message))
            except Exception:
                disconnected.add((websocket, user_id))
        
        for conn in disconnected:
            self.reminder_connections.discard(conn)

    async def send_to_user(self, user_id: int, message: dict[str, Any]):
        """Send a message to a specific user across all their connections."""
        disconnected = set()
        
        # Send to global connections
        for websocket, uid in list(self.global_connections):
            if uid == user_id:
                try:
                    await websocket.send_json(self._format_message(message))
                except Exception:
                    disconnected.add(('global', websocket, uid))
        
        # Send to task connections
        for task_id in list(self.task_connections.keys()):
            for websocket, uid in list(self.task_connections[task_id]):
                if uid == user_id:
                    try:
                        await websocket.send_json(self._format_message(message))
                    except Exception:
                        disconnected.add(('task', task_id, websocket, uid))
        
        # Send to reminder connections
        for websocket, uid in list(self.reminder_connections):
            if uid == user_id:
                try:
                    await websocket.send_json(self._format_message(message))
                except Exception:
                    disconnected.add(('reminder', websocket, uid))
        
        # Clean up disconnected connections
        for item in disconnected:
            if item[0] == 'global':
                self.global_connections.discard((item[1], item[2]))
            elif item[0] == 'task':
                self.task_connections[item[1]].discard((item[2], item[3]))
            elif item[0] == 'reminder':
                self.reminder_connections.discard((item[1], item[2]))

    @staticmethod
    def _format_message(message: dict[str, Any]) -> dict[str, Any]:
        """Format a message with timestamp."""
        return {
            **message,
            "ts": datetime.utcnow().isoformat()
        }


# Global instance
manager = ConnectionManager()
