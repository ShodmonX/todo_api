from fastapi import APIRouter, Depends, HTTPException

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.api.v1.deps import check_task_access, ensure_comment_access
from app.schemas import CommentOut, CommentCreate, CommentUpdate
from app.crud import (
    update_comment,
    delete_comment,
)
from app.models import User, Comment


router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


@router.get("/{comment_id}", response_model=CommentOut)
async def get_comment_info(
    comment: Annotated[Comment, Depends(ensure_comment_access)],
):
    return comment


@router.put("/{comment_id}", response_model=CommentOut)
async def update_comment_by_id(
    comment: Annotated[Comment, Depends(ensure_comment_access)],
    update_data: CommentUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    # Enforce author-only update
    if comment.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="You can only update your own comments")
    
    updated_comment = await update_comment(session, comment, update_data)
    return updated_comment


@router.delete("/{comment_id}")
async def delete_comment_by_id(
    comment: Annotated[Comment, Depends(ensure_comment_access)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    # Enforce author-only delete
    if comment.user_id != user.id and not user.is_superuser:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    await delete_comment(session, comment.id)
    return {"status": "ok", "message": "Comment deleted"}
