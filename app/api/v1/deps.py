from fastapi import Depends, HTTPException

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Task, Attachment
from app.crud import get_task_by_task_id, get_attachment_by_id, get_subtask

async def check_task_access(
    task_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Task:
    task = await get_task_by_task_id(session, task_id)
    
    if user.is_superuser or task.user_id == user.id:
        return task
    
    raise HTTPException(
        status_code=403, 
        detail="You do not have permission to access this task"
    )


async def ensure_attachment_access(
    attachment_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> Attachment:
    attachment = await get_attachment_by_id(session, attachment_id)
    await check_task_access(attachment.task_id, user, session)
    return attachment


async def ensure_subtask_access(
    subtask_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    from app.models import Subtask
    subtask = await get_subtask(session, subtask_id)
    await check_task_access(subtask.task_id, user, session)
    return subtask