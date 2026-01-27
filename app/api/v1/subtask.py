from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.v1.deps import ensure_subtask_access
from app.schemas import SubtaskOut, SubtaskCreate, SubtaskUpdate
from app.crud import (
    update_subtask,
    delete_subtask,
)
from app.models import Subtask


router = APIRouter(
    prefix="/subtasks",
    tags=["Subtasks"],
)


@router.get("/{subtask_id}", response_model=SubtaskOut)
async def get_subtask_info(
    subtask: Annotated[Subtask, Depends(ensure_subtask_access)],
):
    return subtask


@router.put("/{subtask_id}", response_model=SubtaskOut)
async def update_subtask_by_id(
    subtask: Annotated[Subtask, Depends(ensure_subtask_access)],
    update_data: SubtaskUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    updated_subtask = await update_subtask(session, subtask, update_data)
    return updated_subtask


@router.delete("/{subtask_id}")
async def delete_subtask_by_id(
    subtask: Annotated[Subtask, Depends(ensure_subtask_access)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    await delete_subtask(session, subtask.id)
    return {"status": "ok", "message": "Subtask deleted"}
