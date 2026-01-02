from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.schemas import TaskIn, TaskOutResponse, TaskOut
from app.crud import create_task, get_all_tasks_of_user, get_task_by_task_id
from app.database import get_db
from app.models import User


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=TaskOutResponse)
async def add_task(
    task: Annotated[TaskIn, TaskIn],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    task_db = await create_task(session, task, user)
    return {
        "status": "ok",
        "message": "Task created",
        "task": task_db
    }

@router.get("/", response_model=list[TaskOut])
async def read_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    tasks = await get_all_tasks_of_user(session, user)
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def read_task(
    task_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    task = await get_task_by_task_id(session, task_id)
    if task.user_id != user.id:
        raise HTTPException(status_code=405, detail="You are not allowed to this task")
    return task