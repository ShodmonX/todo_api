from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from fastapi import HTTPException

from app.models import Task, User
from app.schemas import TaskIn, TaskUpdate, StatusEnum, PriorityEnum


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

