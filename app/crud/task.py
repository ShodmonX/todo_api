from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, or_, func

from fastapi import HTTPException
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import calendar

from app.models import Task, User
from app.schemas import TaskIn, TaskUpdate, StatusEnum, PriorityEnum, TaskBulkUpdateStatus


async def create_task(session: AsyncSession, task: TaskIn, user: User):
    task_db = Task(**task.model_dump(), user = user)

    try:
        session.add(task_db)
        await session.commit()
        await session.refresh(task_db)
        return task_db
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def create_bulk_task(session: AsyncSession, tasks: list[TaskIn], user: User):
    task_dbs = [Task(**task.model_dump(), user = user) for task in tasks]
    try:
        session.add_all(task_dbs)
        await session.commit()
        return task_dbs
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_all_tasks_of_user(session: AsyncSession, user: User, status: StatusEnum | None = None, priority: PriorityEnum | None = None):
    stmt = select(Task).where(Task.user_id == user.id)
    if status is not None:
        stmt = stmt.where(Task.status == status.value)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority.value)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_task_by_task_id(session: AsyncSession, task_id: int):
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

async def update_task(session: AsyncSession, task_id: int, task_update: TaskUpdate):
    values_to_update = task_update.model_dump(exclude_unset=True)
    if not values_to_update:
         return await get_task_by_task_id(session, task_id)
    stmt = update(Task).where(Task.id == task_id).values(**values_to_update).returning(Task)
    try:
        result = await session.execute(stmt)
        updated_task = result.scalars().first()
        if not updated_task:
            raise HTTPException(status_code=404, detail="Task not found")
        await session.commit()
        return updated_task
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def delete_task(session: AsyncSession, task_id: int):
    stmt = delete(Task).where(Task.id == task_id)
    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def delete_bulk_task(session: AsyncSession, task_ids: list[int], user: User):
    stmt = select(Task).where(and_(Task.id.in_(task_ids), Task.user_id == user.id))
    try:
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        if not tasks:
            raise HTTPException(status_code=404, detail="Tasks not found")

        for task in tasks:
            await session.delete(task)
            
        await session.commit()
        return {
            "deleted_task_count": len(tasks)
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_status_bulk(session: AsyncSession, update_status: TaskBulkUpdateStatus, user: User):
    stmt = update(Task).where(and_(Task.id.in_(update_status.ids), Task.user_id == user.id)).values(status=update_status.status).returning(Task)

    try:
        result = await session.execute(stmt)

        tasks = result.scalars().all()

        if not tasks:
            raise HTTPException(status_code=404, detail="Task not found.")
        
        await session.commit()
        return tasks
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def update_status(session: AsyncSession, task_id: int, status: str):
    stmt = update(Task).where(Task.id == task_id).values(status = status).returning(Task)
    try:
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().one()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_priority(session: AsyncSession, task_id: int, priority: str):
    stmt = update(Task).where(Task.id == task_id).values(priority = priority).returning(Task)
    try:
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().one()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def search_tasks(session: AsyncSession, user: User, query: str, status: StatusEnum | None = None, priority: PriorityEnum | None = None):
    stmt = select(Task).where(and_(or_(Task.title.ilike(f"%{query}%"), Task.description.ilike(f"%{query}%")), Task.user_id == user.id))
    if status is not None:
        stmt = stmt.where(Task.status == status.value)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority.value)
    result = await session.execute(stmt)
    return result.scalars().all()
        
async def get_task_statistics(session: AsyncSession, user: User) -> dict[str, int | dict[str, int]]:
    total_tasks = await session.scalar(select(func.count()).where(Task.user_id == user.id)) or 0
    pending_tasks = await session.scalar(select(func.count()).where(and_(Task.status == "pending", Task.user_id == user.id))) or 0
    in_progress_tasks = await session.scalar(select(func.count()).where(and_(Task.status == "in_progress", Task.user_id == user.id))) or 0
    completed_tasks = await session.scalar(select(func.count()).where(and_(Task.status == "completed", Task.user_id == user.id))) or 0
    low_tasks = await session.scalar(select(func.count()).where(and_(Task.priority == "low", Task.user_id == user.id))) or 0
    medium_tasks = await session.scalar(select(func.count()).where(and_(Task.priority == "medium", Task.user_id == user.id))) or 0
    high_tasks = await session.scalar(select(func.count()).where(and_(Task.priority == "high", Task.user_id == user.id))) or 0

    return {
        "total_tasks": total_tasks,
        "status": {
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks
        },
        "priority": {
            "low": low_tasks,
            "medium": medium_tasks,
            "high": high_tasks
        }
    }

async def get_todays_tasks(session: AsyncSession, user: User):
    now = datetime.now(ZoneInfo(user.timezone))
    today = now.date()

    stmt = select(Task).where(and_(Task.due_date == today, Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()

async def get_tomorrows_tasks(session: AsyncSession, user: User):
    tomorrow = datetime.now(ZoneInfo(user.timezone)) + timedelta(days=1)
    today = tomorrow.date()

    stmt = select(Task).where(and_(Task.due_date == today, Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()

async def get_this_weeks_tasks(session: AsyncSession, user: User):
    now = datetime.now(ZoneInfo(user.timezone))
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = now + timedelta(days=6)


    stmt = select(Task).where(and_(Task.due_date >= start_of_week.date(), Task.due_date <= end_of_week.date(), Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()

async def get_this_months_tasks(session: AsyncSession, user: User):
    now = datetime.now(ZoneInfo(user.timezone))
    start_of_month= now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
    _, num_days = calendar.monthrange(now.year, now.month)
    end_of_month = now.replace(day=num_days, hour=23, minute=59, second=59, microsecond=99999).date()


    stmt = select(Task).where(and_(Task.due_date >= start_of_month, Task.due_date <= end_of_month, Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()

async def get_overdue_tasks(session: AsyncSession, user: User):
    now = datetime.now(ZoneInfo(user.timezone)).date()

    stmt = select(Task).where(and_(Task.due_date < now, Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()

async def get_tasks_by_status(session: AsyncSession, user: User, status: str):
    stmt = select(Task).where(and_(Task.status == status, Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()

async def get_tasks_by_priority(session: AsyncSession, user: User, priority: str):
    stmt = select(Task).where(and_(Task.priority == priority, Task.user_id == user.id))
    result = await session.execute(stmt)

    return result.scalars().all()
