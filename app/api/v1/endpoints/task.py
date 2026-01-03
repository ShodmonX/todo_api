from fastapi import APIRouter, Depends, Body, Query

from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.schemas import TaskIn, TaskOutResponse, TaskOut, TaskUpdate, StatusEnum, PriorityEnum
from app.crud import create_task, get_all_tasks_of_user, update_task, delete_task, update_priority, update_status
from app.database import get_db
from app.models import User, Task
from app.api.v1.deps import check_task_access


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
    session: Annotated[AsyncSession, Depends(get_db)],
    status: Annotated[StatusEnum | None, Query()] = None,
    priority: Annotated[PriorityEnum | None, Query()] = None
):
    tasks = await get_all_tasks_of_user(session, user, status, priority)
    return tasks

@router.get("/{task_id}", response_model=TaskOut)
async def read_task(
    task: Annotated[Task, Depends(check_task_access)],
):
    return task

@router.put("/{task_id}", response_model=TaskOutResponse)
async def update_task_by_id(
    task: Annotated[Task, Depends(check_task_access)],
    task_update: Annotated[TaskUpdate, TaskUpdate],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    task_updated = await update_task(session, task.id, task_update)
    return {
        "status": "ok",
        "message": "Task updated",
        "task": task_updated
    }

@router.delete("/{task_id}")
async def delete_task_by_id(
    task: Annotated[Task, Depends(check_task_access)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    await delete_task(session, task.id)
    return task

@router.patch("/{task_id}/status")
async def update_status_of_task_by_id(
    task: Annotated[Task, Depends(check_task_access)],
    session: Annotated[AsyncSession, Depends(get_db)],
    status: Annotated[StatusEnum, Body()]
):
    task = await update_status(session, task.id, status)
    return task

@router.patch("/{task_id}/priority")
async def update_priority_of_task_by_id(
    task: Annotated[Task, Depends(check_task_access)],
    session: Annotated[AsyncSession, Depends(get_db)],
    priority: Annotated[PriorityEnum, Body()]
):
    task = await update_priority(session, task.id, priority)
    return task