from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.schemas import ReminderOut, ReminderCreate, ReminderUpdate, TaskReminderCreate
from app.crud import (
    list_reminders,
    get_reminder,
    create_reminder,
    update_reminder,
    delete_reminder,
    list_upcoming_reminders
)
from app.database import get_db
from app.models import User, Task
from app.api.v1.deps import check_task_access


router = APIRouter(
    prefix="/reminders",
    tags=["reminders"]
)


@router.get("/", response_model=list[ReminderOut])
async def get_all_reminders(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> list[ReminderOut]:
    """Get all reminders for current user."""
    reminders = await list_reminders(session, user.id)
    return reminders


@router.post("/", response_model=ReminderOut, status_code=201)
async def create_reminder_endpoint(
    reminder_data: ReminderCreate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ReminderOut:
    """Create a new reminder."""
    # If task_id is provided, verify user has access to that task
    if reminder_data.task_id:
        try:
            await check_task_access(reminder_data.task_id, user, session)
        except HTTPException:
            raise HTTPException(status_code=403, detail="You do not have access to this task")
    
    reminder = await create_reminder(session, reminder_data)
    return reminder


@router.get("/upcoming", response_model=list[ReminderOut])
async def get_upcoming_reminders(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[ReminderOut]:
    """Get upcoming unsent reminders (soonest first)."""
    reminders = await list_upcoming_reminders(session, user.id, limit)
    return reminders


@router.get("/{reminder_id}", response_model=ReminderOut)
async def get_reminder_endpoint(
    reminder_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ReminderOut:
    """Get a specific reminder."""
    reminder = await get_reminder(session, reminder_id)
    
    # Enforce access control
    if reminder.task_id:
        try:
            await check_task_access(reminder.task_id, user, session)
        except HTTPException:
            raise HTTPException(status_code=403, detail="You do not have access to this reminder")
    
    return reminder


@router.put("/{reminder_id}", response_model=ReminderOut)
async def update_reminder_endpoint(
    reminder_id: int,
    update_data: ReminderUpdate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> ReminderOut:
    """Update a reminder."""
    reminder = await get_reminder(session, reminder_id)
    
    # Enforce access control
    if reminder.task_id:
        try:
            await check_task_access(reminder.task_id, user, session)
        except HTTPException:
            raise HTTPException(status_code=403, detail="You do not have access to this reminder")
    
    updated_reminder = await update_reminder(session, reminder, update_data)
    return updated_reminder


@router.delete("/{reminder_id}")
async def delete_reminder_endpoint(
    reminder_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """Delete a reminder."""
    reminder = await get_reminder(session, reminder_id)
    
    # Enforce access control
    if reminder.task_id:
        try:
            await check_task_access(reminder.task_id, user, session)
        except HTTPException:
            raise HTTPException(status_code=403, detail="You do not have access to this reminder")
    
    await delete_reminder(session, reminder_id)
    return {
        "status": "ok",
        "message": "Reminder deleted"
    }
