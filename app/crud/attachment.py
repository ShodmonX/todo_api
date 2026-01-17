from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Attachment


async def get_all_attachment_of_task(session: AsyncSession, task_id: int):
    stmt = select(Attachment).where(Attachment.task_id == task_id)
    result = await session.execute(stmt)
    return result.scalars().all()

async def add_attachment_to_task(session: AsyncSession, task_id: int):
    return