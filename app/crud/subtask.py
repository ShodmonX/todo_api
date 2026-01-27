from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from datetime import datetime, timezone
from fastapi import HTTPException

from app.models import Subtask
from app.schemas import SubtaskCreate, SubtaskUpdate


async def list_subtasks_by_task(session: AsyncSession, task_id: int) -> list[Subtask]:
    stmt = select(Subtask).where(Subtask.task_id == task_id).order_by(Subtask.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_subtask(
    session: AsyncSession,
    task_id: int,
    subtask_data: SubtaskCreate
) -> Subtask:
    completed_at = datetime.now(timezone.utc) if subtask_data.is_completed else None
    
    subtask = Subtask(
        title=subtask_data.title,
        is_completed=subtask_data.is_completed,
        task_id=task_id,
        completed_at=completed_at
    )
    
    try:
        session.add(subtask)
        await session.commit()
        await session.refresh(subtask)
        return subtask
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def get_subtask(session: AsyncSession, subtask_id: int) -> Subtask:
    stmt = select(Subtask).where(Subtask.id == subtask_id)
    result = await session.execute(stmt)
    subtask = result.scalars().first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return subtask


async def update_subtask(
    session: AsyncSession,
    subtask: Subtask,
    update_data: SubtaskUpdate
) -> Subtask:
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        return subtask
    
    # Handle completed_at logic
    if 'is_completed' in update_dict:
        new_is_completed = update_dict['is_completed']
        old_is_completed = subtask.is_completed
        
        if new_is_completed and not old_is_completed:
            # Transition from False to True
            update_dict['completed_at'] = datetime.now(timezone.utc)
        elif not new_is_completed and old_is_completed:
            # Transition from True to False
            update_dict['completed_at'] = None
    
    # Apply updates
    for key, value in update_dict.items():
        setattr(subtask, key, value)
    
    try:
        await session.commit()
        await session.refresh(subtask)
        return subtask
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def delete_subtask(session: AsyncSession, subtask_id: int) -> None:
    stmt = delete(Subtask).where(Subtask.id == subtask_id)
    try:
        result = await session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Subtask not found")
        await session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
