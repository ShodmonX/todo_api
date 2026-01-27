from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from fastapi import HTTPException

from app.models import Attachment
from app.schemas import MimeTypeEnum


async def get_all_attachment_of_task(session: AsyncSession, task_id: int):
    stmt = select(Attachment).where(Attachment.task_id == task_id).order_by(Attachment.uploaded_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_attachment_by_id(session: AsyncSession, attachment_id: int) -> Attachment:
    stmt = select(Attachment).where(Attachment.id == attachment_id)
    result = await session.execute(stmt)
    attachment = result.scalars().first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return attachment


async def create_attachment(
    session: AsyncSession,
    *,
    filename: str,
    file_path: str,
    file_size: int,
    mime_type: MimeTypeEnum,
    task_id: int,
    user_id: int,
) -> Attachment:
    attachment = Attachment(
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        task_id=task_id,
        user_id=user_id,
    )
    try:
        session.add(attachment)
        await session.commit()
        await session.refresh(attachment)
        return attachment
    except Exception as exc:  # pragma: no cover - defensive rollback
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))


async def delete_attachment(session: AsyncSession, attachment_id: int) -> None:
    stmt = delete(Attachment).where(Attachment.id == attachment_id)
    try:
        result = await session.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Attachment not found")
        await session.commit()
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive rollback
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(exc))