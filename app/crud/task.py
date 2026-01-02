from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import HTTPException

from app.models import Task, User
from app.schemas import TaskIn


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
    
async def get_all_tasks_of_user(session: AsyncSession, user: User):
    stmt = select(Task).where(Task.user_id == user.id)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_task_by_task_id(session: AsyncSession, task_id: int):
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

