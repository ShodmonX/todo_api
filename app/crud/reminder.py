from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, and_

from datetime import datetime
from fastapi import HTTPException

from app.models import Reminder, Task
from app.schemas import ReminderCreate, ReminderUpdate


async def list_reminders(session: AsyncSession, user_id: int) -> list[Reminder]:
    """List all reminders for a user (through task access)."""
    stmt = (
        select(Reminder)
        .join(Task, Reminder.task_id == Task.id, isouter=True)
        .where(
            (Task.user_id == user_id) | (Reminder.task_id.is_(None))
        )
        .order_by(Reminder.reminder_time.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_reminder(session: AsyncSession, reminder_id: int) -> Reminder:
    """Get a reminder by ID."""
    stmt = select(Reminder).where(Reminder.id == reminder_id)
    result = await session.execute(stmt)
    reminder = result.scalars().first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


async def create_reminder(
    session: AsyncSession,
    reminder_data: ReminderCreate
) -> Reminder:
    """Create a new reminder."""
    reminder = Reminder(
        task_id=reminder_data.task_id,
        reminder_time=reminder_data.reminder_time,
        is_sent=False
    )
    
    try:
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)
        return reminder
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def update_reminder(
    session: AsyncSession,
    reminder: Reminder,
    update_data: ReminderUpdate
) -> Reminder:
    """Update an existing reminder."""
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        return reminder
    
    # Handle is_sent state transitions
    if 'is_sent' in update_dict:
        new_is_sent = update_dict['is_sent']
        
        if new_is_sent and not reminder.is_sent:
            # Transition from False to True
            update_dict['sent_at'] = datetime.utcnow()
        elif not new_is_sent and reminder.is_sent:
            # Transition from True to False
            update_dict['sent_at'] = None
    
    for key, value in update_dict.items():
        setattr(reminder, key, value)
    
    try:
        await session.commit()
        await session.refresh(reminder)
        return reminder
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def delete_reminder(session: AsyncSession, reminder_id: int) -> None:
    """Delete a reminder."""
    stmt = delete(Reminder).where(Reminder.id == reminder_id)
    try:
        result = await session.execute(stmt)
        if result.rowcount == 0:  # type: ignore
            raise HTTPException(status_code=404, detail="Reminder not found")
        await session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def list_upcoming_reminders(
    session: AsyncSession,
    user_id: int,
    limit: int = 20
) -> list[Reminder]:
    """List upcoming unsent reminders (reminder_time >= now, is_sent = False) for a user."""
    now = datetime.utcnow()
    stmt = (
        select(Reminder)
        .join(Task, Reminder.task_id == Task.id, isouter=True)
        .where(
            and_(
                Reminder.reminder_time >= now,
                Reminder.is_sent == False,
                (Task.user_id == user_id) | (Reminder.task_id.is_(None))
            )
        )
        .order_by(Reminder.reminder_time.asc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
