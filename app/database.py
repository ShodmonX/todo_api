from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    settings.DATABASE_URL,
    future=True
)

SessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()