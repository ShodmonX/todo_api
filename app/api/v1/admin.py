"""
Admin API endpoints for dashboard, backup, logs, and settings management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Annotated, Any
from datetime import datetime
from pathlib import Path
import json
import shutil
import os

from app.database import get_db, engine
from app.dependencies import get_admin
from app.models import User, Task, Category, Attachment, Subtask, Comment, Reminder
from app.schemas.admin import (
    AdminDashboardOut,
    AdminSettingsOut,
    AdminSettingsUpdate,
    BackupOut
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_admin)]
)

# Configuration
BACKUP_ROOT = Path("backups")
BACKUP_ROOT.mkdir(exist_ok=True)


@router.get("/dashboard", response_model=AdminDashboardOut)
async def get_admin_dashboard(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> AdminDashboardOut:
    """
    Get admin dashboard statistics.
    
    Returns counts for all main entities and database information.
    """
    try:
        # Get counts for each model
        users_count = await session.scalar(select(func.count(User.id)))
        tasks_count = await session.scalar(select(func.count(Task.id)))
        categories_count = await session.scalar(select(func.count(Category.id)))
        attachments_count = await session.scalar(select(func.count(Attachment.id)))
        subtasks_count = await session.scalar(select(func.count(Subtask.id)))
        comments_count = await session.scalar(select(func.count(Comment.id)))
        reminders_count = await session.scalar(select(func.count(Reminder.id)))
        
        # Get database info
        db_dialect = engine.dialect.name
        
        # Get active users count (logged in within last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = await session.scalar(
            select(func.count(User.id)).where(User.last_login >= thirty_days_ago)
        )
        
        return AdminDashboardOut(
            users_count=users_count or 0,
            tasks_count=tasks_count or 0,
            categories_count=categories_count or 0,
            attachments_count=attachments_count or 0,
            subtasks_count=subtasks_count or 0,
            comments_count=comments_count or 0,
            reminders_count=reminders_count or 0,
            active_users_count=active_users or 0,
            db_dialect=db_dialect,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")


@router.get("/backup", response_model=BackupOut)
async def create_database_backup(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> BackupOut:
    """
    Create a database backup (PostgreSQL).
    
    For PostgreSQL, creates a JSON export of key tables.
    Returns metadata about the backup file.
    """
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.json"
        backup_path = BACKUP_ROOT / backup_filename
        
        # Export data from all tables to JSON
        backup_data = {
            "backup_metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "database_type": "postgresql",
                "version": "1.0"
            },
            "users": [],
            "tasks": [],
            "categories": [],
            "attachments": [],
            "subtasks": [],
            "comments": [],
            "reminders": []
        }
        
        # Export users (exclude sensitive data)
        users = await session.execute(select(User))
        for user in users.scalars():
            backup_data["users"].append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "timezone": user.timezone
            })
        
        # Export tasks
        tasks = await session.execute(select(Task))
        for task in tasks.scalars():
            backup_data["tasks"].append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "user_id": task.user_id,
                "category_id": task.category_id,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "due_date": task.due_date.isoformat() if task.due_date else None
            })
        
        # Export categories
        categories = await session.execute(select(Category))
        for category in categories.scalars():
            backup_data["categories"].append({
                "id": category.id,
                "name": category.name,
                "user_id": category.user_id,
                "created_at": category.created_at.isoformat() if category.created_at else None
            })
        
        # Export attachments
        attachments = await session.execute(select(Attachment))
        for attachment in attachments.scalars():
            backup_data["attachments"].append({
                "id": attachment.id,
                "filename": attachment.filename,
                "file_path": attachment.file_path,
                "mime_type": attachment.mime_type,
                "file_size": attachment.file_size,
                "task_id": attachment.task_id,
                "user_id": attachment.user_id,
                "created_at": attachment.created_at.isoformat() if attachment.created_at else None
            })
        
        # Export subtasks
        subtasks = await session.execute(select(Subtask))
        for subtask in subtasks.scalars():
            backup_data["subtasks"].append({
                "id": subtask.id,
                "title": subtask.title,
                "is_completed": subtask.is_completed,
                "task_id": subtask.task_id,
                "created_at": subtask.created_at.isoformat() if subtask.created_at else None,
                "updated_at": subtask.updated_at.isoformat() if subtask.updated_at else None
            })
        
        # Export comments
        comments = await session.execute(select(Comment))
        for comment in comments.scalars():
            backup_data["comments"].append({
                "id": comment.id,
                "content": comment.content,
                "task_id": comment.task_id,
                "user_id": comment.user_id,
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
                "updated_at": comment.updated_at.isoformat() if comment.updated_at else None
            })
        
        # Export reminders
        reminders = await session.execute(select(Reminder))
        for reminder in reminders.scalars():
            backup_data["reminders"].append({
                "id": reminder.id,
                "message": reminder.message,
                "remind_at": reminder.remind_at.isoformat() if reminder.remind_at else None,
                "is_sent": reminder.is_sent,
                "task_id": reminder.task_id,
                "created_at": reminder.created_at.isoformat() if reminder.created_at else None
            })
        
        # Write backup to file
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        file_size = backup_path.stat().st_size
        
        return BackupOut(
            detail="Backup created successfully",
            backup_path=str(backup_path),
            backup_filename=backup_filename,
            created_at=datetime.utcnow(),
            file_size=file_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")


@router.post("/restore")
async def restore_database(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, str]:
    """
    Restore database from backup.
    
    NOTE: This is a sensitive operation. For PostgreSQL databases,
    manual restore using pg_restore is recommended for production.
    
    This endpoint returns 501 (Not Implemented) for safety.
    """
    raise HTTPException(
        status_code=501,
        detail="Database restore must be performed manually using pg_restore. "
               "Please use: pg_restore -U admin -d todo < backup_file"
    )


@router.get("/logs")
async def get_application_logs(
    lines: Annotated[int, Query(ge=1, le=5000)] = 200,
    level: Annotated[str | None, Query()] = None
) -> dict[str, Any]:
    """
    Get application logs.
    
    Returns recent log entries. By default returns last 200 lines.
    
    Args:
        lines: Number of lines to return (1-5000, default 200)
        level: Filter by log level (optional)
    """
    # Check if log file exists (configured log path)
    log_file_path = Path("logs/app.log")
    
    if not log_file_path.exists():
        # Return a message that file logging is not configured
        return {
            "detail": "File logging not configured. Application logs to stdout only.",
            "logs": [],
            "total_lines": 0
        }
    
    try:
        # Read last N lines efficiently
        with open(log_file_path, 'r') as f:
            # Read all lines and get last N
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Filter by level if specified
            if level:
                level_upper = level.upper()
                recent_lines = [line for line in recent_lines if level_upper in line]
            
            return {
                "detail": "Logs retrieved successfully",
                "logs": [line.strip() for line in recent_lines],
                "total_lines": len(recent_lines),
                "requested_lines": lines,
                "filter_level": level
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {str(e)}")


@router.get("/settings", response_model=AdminSettingsOut)
async def get_application_settings(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> AdminSettingsOut:
    """
    Get application settings.
    
    Returns safe, non-sensitive application configuration.
    """
    from app.config import settings
    
    return AdminSettingsOut(
        api_title=settings.API_TITLE,
        api_version=settings.API_VERSION,
        debug=settings.DEBUG,
        media_root=settings.MEDIA_ROOT,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


@router.put("/settings", response_model=AdminSettingsOut)
async def update_application_settings(
    settings_update: AdminSettingsUpdate,
    session: Annotated[AsyncSession, Depends(get_db)]
) -> AdminSettingsOut:
    """
    Update application settings.
    
    NOTE: This endpoint is limited to read-only configuration display.
    Most settings are environment-based and cannot be changed via API.
    
    Returns 501 (Not Implemented).
    """
    raise HTTPException(
        status_code=501,
        detail="Settings update not implemented. Application settings are environment-based. "
               "Please update .env file and restart the application."
    )
