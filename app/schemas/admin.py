"""
Admin API schemas for dashboard, backup, logs, and settings.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AdminDashboardOut(BaseModel):
    """Admin dashboard statistics."""
    users_count: int = Field(..., description="Total number of users")
    tasks_count: int = Field(..., description="Total number of tasks")
    categories_count: int = Field(..., description="Total number of categories")
    attachments_count: int = Field(..., description="Total number of attachments")
    subtasks_count: int = Field(..., description="Total number of subtasks")
    comments_count: int = Field(..., description="Total number of comments")
    reminders_count: int = Field(..., description="Total number of reminders")
    active_users_count: int = Field(..., description="Users active in last 30 days")
    db_dialect: str = Field(..., description="Database dialect (postgresql, mysql, etc.)")
    timestamp: datetime = Field(..., description="Timestamp of dashboard data")


class BackupOut(BaseModel):
    """Backup creation response."""
    detail: str = Field(..., description="Status message")
    backup_path: str = Field(..., description="Path to backup file")
    backup_filename: str = Field(..., description="Backup filename")
    created_at: datetime = Field(..., description="Backup creation timestamp")
    file_size: int = Field(..., description="Backup file size in bytes")


class AdminSettingsOut(BaseModel):
    """Safe application settings (non-sensitive)."""
    api_title: str = Field(..., description="API title")
    api_version: str = Field(..., description="API version")
    debug: bool = Field(..., description="Debug mode enabled")
    media_root: str = Field(..., description="Media files root directory")
    access_token_expire_minutes: int = Field(..., description="Access token expiration in minutes")
    refresh_token_expire_days: int = Field(..., description="Refresh token expiration in days")


class AdminSettingsUpdate(BaseModel):
    """Settings update schema (currently not implemented)."""
    # Placeholder for future settings that can be updated via API
    # Currently returns 501 Not Implemented
    pass
