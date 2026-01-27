from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from datetime import datetime, timezone
from fastapi import HTTPException

from app.models import Comment
from app.schemas import CommentCreate, CommentUpdate


async def list_comments_by_task(session: AsyncSession, task_id: int) -> list[Comment]:
    stmt = select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def create_comment(
    session: AsyncSession,
    task_id: int,
    user_id: int,
    comment_data: CommentCreate
) -> Comment:
    comment = Comment(
        content=comment_data.content,
        task_id=task_id,
        user_id=user_id
    )
    
    try:
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def get_comment(session: AsyncSession, comment_id: int) -> Comment:
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await session.execute(stmt)
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


async def update_comment(
    session: AsyncSession,
    comment: Comment,
    update_data: CommentUpdate
) -> Comment:
    comment.content = update_data.content
    comment.updated_at = datetime.utcnow()
    
    try:
        await session.commit()
        await session.refresh(comment)
        return comment
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def delete_comment(session: AsyncSession, comment_id: int) -> None:
    stmt = delete(Comment).where(Comment.id == comment_id)
    try:
        result = await session.execute(stmt)
        if result.rowcount == 0: #type: ignore
            raise HTTPException(status_code=404, detail="Comment not found")
        await session.commit()
    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))
