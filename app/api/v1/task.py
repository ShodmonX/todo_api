from fastapi import APIRouter, Depends, Body, Query, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.dependencies import get_current_user
from app.schemas import TaskIn, TaskOutResponse, TaskOut, TaskUpdate, StatusEnum, PriorityEnum, TaskOutBulkResponse, TaskBulkUpdateStatus, AttachmentOut, MimeTypeEnum, SubtaskOut, SubtaskCreate, CommentOut, CommentCreate
from app.crud import create_task, get_all_tasks_of_user, update_task, delete_task, update_priority, update_status, create_bulk_task, delete_bulk_task, \
                     update_status_bulk, search_tasks, get_task_statistics, get_todays_tasks, get_tomorrows_tasks, get_this_weeks_tasks, get_this_months_tasks, \
                     get_overdue_tasks, get_tasks_by_status, get_tasks_by_priority, \
                     get_all_attachment_of_task, create_attachment, get_attachment_by_id, delete_attachment, \
                     list_subtasks_by_task, create_subtask, \
                     list_comments_by_task, create_comment
from app.database import get_db
from app.models import User, Task
from app.api.v1.deps import check_task_access
from app.config import settings
from app.utils.storage import build_storage_paths, save_upload_file


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

MEDIA_ROOT = Path(settings.MEDIA_ROOT)

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

@router.get("/search", response_model=list[TaskOut])
async def search_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    query: Annotated[str, Query()],
    status: Annotated[StatusEnum | None, Query()] = None,
    priority: Annotated[PriorityEnum | None, Query()] = None,
):
    tasks = await search_tasks(session, user, query, status, priority)
    return tasks

@router.get("/statistics")
async def get_statistics(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, int | dict[str, int]]:
    return await get_task_statistics(session, user)

@router.get("/overdue", response_model=TaskOutBulkResponse)
async def get_overdue_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_overdue_tasks(session, user)

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any overdue tasks.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} overdue tasks found.",
        "tasks": tasks
    }

@router.get("/pending", response_model=TaskOutBulkResponse)
async def get_pending_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tasks_by_status(session, user, "pending")

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks with 'pending' status.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks found with 'pending' status.",
        "tasks": tasks
    }

@router.get("/in-progress", response_model=TaskOutBulkResponse)
async def get_in_progress_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tasks_by_status(session, user, "in_progress")

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks with 'in_progress' status.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks found with 'in_progress' status.",
        "tasks": tasks
    }

@router.get("/completed", response_model=TaskOutBulkResponse)
async def get_completed_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tasks_by_status(session, user, "completed")

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks with 'completed' status.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks found with 'completed' status.",
        "tasks": tasks
    }

@router.get("/priority/low", response_model=TaskOutBulkResponse)
async def get_low_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tasks_by_priority(session, user, "low")

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks with 'low' priority.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks found with 'low' priority.",
        "tasks": tasks
    }

@router.get("/priority/medium", response_model=TaskOutBulkResponse)
async def get_medium_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tasks_by_priority(session, user, "medium")

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks with 'medium' priority.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks found with 'medium' priority.",
        "tasks": tasks
    }

@router.get("/priority/high", response_model=TaskOutBulkResponse)
async def get_high_all_tasks(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tasks_by_priority(session, user, "high")

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks with 'high' priority.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks found with 'high' priority.",
        "tasks": tasks
    }

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

@router.post("/bulk", response_model=TaskOutBulkResponse)
async def create_tasks(
    tasks: Annotated[list[TaskIn], list[TaskIn]],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    created_tasks = await create_bulk_task(session, tasks, user)
    return {
        "status": "ok",
        "message": "Tasks created",
        "tasks": created_tasks
    }

@router.delete("/bulk")
async def delete_tasks(
    task_ids: Annotated[list[int], Body(..., embed=True)],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    data = await delete_bulk_task(session, task_ids, user)
    if not data:
        raise HTTPException(status_code=404, detail="Task not found.")
    return data

@router.post("/bulk/status", response_model=TaskOutBulkResponse)
async def update_status_bulk_by_ids(
    update_status: Annotated[TaskBulkUpdateStatus, Body()],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await update_status_bulk(session, update_status, user)

    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tasks updated",
        "tasks": tasks
    }

@router.get("/due/today", response_model=TaskOutBulkResponse)
async def get_todays_all_task(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_todays_tasks(session, user)

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks for today.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} today's tasks found.",
        "tasks": tasks
    }

@router.get("/due/tomorrow", response_model=TaskOutBulkResponse)
async def get_tomorrows_all_task(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_tomorrows_tasks(session, user)

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks for tomorrow.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} tomorrow's tasks found.",
        "tasks": tasks
    }

@router.get("/due/this-week", response_model=TaskOutBulkResponse)
async def get_weeks_all_task(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_this_weeks_tasks(session, user)

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks for this week.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} this week's tasks found.",
        "tasks": tasks
    }

@router.get("/due/this-month", response_model=TaskOutBulkResponse)
async def get_months_all_task(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    tasks = await get_this_months_tasks(session, user)

    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have any tasks for month.")
    
    return {
        "status": "ok",
        "message": f"Total {len(tasks)} this month's tasks found.",
        "tasks": tasks
    }

@router.get("/{task_id}/attachments", response_model=list[AttachmentOut])
async def get_all_attachments_of_task(
    task: Annotated[Task, Depends(check_task_access)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    return await get_all_attachment_of_task(session, task.id)

@router.post("/{task_id}/attachments", response_model=AttachmentOut, status_code=201)
async def upload_attachment_to_task(
    task: Annotated[Task, Depends(check_task_access)],
    file: Annotated[UploadFile, File(...)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    original_filename = file.filename or "uploaded_file"
    allowed_types = [mime.value for mime in MimeTypeEnum]
    if not file.content_type or file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    abs_path, rel_path = build_storage_paths(task.id, original_filename, MEDIA_ROOT)

    try:
        written_size = await save_upload_file(file, abs_path)
    except Exception as exc:  # pragma: no cover - IO guard
        raise HTTPException(status_code=500, detail="Failed to save file") from exc

    try:
        attachment = await create_attachment(
            session,
            filename=original_filename,
            file_path=rel_path,
            file_size=written_size,
            mime_type=MimeTypeEnum(file.content_type),
            task_id=task.id,
            user_id=user.id,
        )
        return attachment
    except HTTPException:
        if abs_path.exists():
            abs_path.unlink()
        raise
    except Exception as exc:  # pragma: no cover - defensive rollback
        if abs_path.exists():
            abs_path.unlink()
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{task_id}/attachments/{attachment_id}/download")
async def download_attachment(
    task: Annotated[Task, Depends(check_task_access)],
    attachment_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    attachment = await get_attachment_by_id(session, attachment_id)
    if attachment.task_id != task.id:
        raise HTTPException(status_code=404, detail="Attachment not found for this task")

    resolved_media_root = MEDIA_ROOT.resolve()
    file_path = (MEDIA_ROOT / attachment.file_path).resolve()
    try:
        file_path.relative_to(resolved_media_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attachment path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type=attachment.mime_type.value,
        filename=attachment.filename,
    )


@router.delete("/{task_id}/attachments/{attachment_id}")
async def delete_attachment_from_task(
    task: Annotated[Task, Depends(check_task_access)],
    attachment_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    attachment = await get_attachment_by_id(session, attachment_id)
    if attachment.task_id != task.id:
        raise HTTPException(status_code=404, detail="Attachment not found for this task")

    resolved_media_root = MEDIA_ROOT.resolve()
    file_path = (MEDIA_ROOT / attachment.file_path).resolve()
    try:
        file_path.relative_to(resolved_media_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attachment path")

    await delete_attachment(session, attachment.id)

    if file_path.exists():
        file_path.unlink()

    return {
        "status": "ok",
        "message": "Attachment deleted",
    }


@router.get("/{task_id}/subtasks", response_model=list[SubtaskOut])
async def get_all_subtasks_of_task(
    task: Annotated[Task, Depends(check_task_access)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    return await list_subtasks_by_task(session, task.id)


@router.post("/{task_id}/subtasks", response_model=SubtaskOut, status_code=201)
async def create_subtask_for_task(
    task: Annotated[Task, Depends(check_task_access)],
    subtask_data: SubtaskCreate,
    session: Annotated[AsyncSession, Depends(get_db)]
):
    subtask = await create_subtask(session, task.id, subtask_data)
    return subtask


@router.get("/{task_id}/comments", response_model=list[CommentOut])
async def get_all_comments_of_task(
    task: Annotated[Task, Depends(check_task_access)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    return await list_comments_by_task(session, task.id)


@router.post("/{task_id}/comments", response_model=CommentOut, status_code=201)
async def create_comment_for_task(
    task: Annotated[Task, Depends(check_task_access)],
    comment_data: CommentCreate,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    comment = await create_comment(session, task.id, user.id, comment_data)
    return comment
