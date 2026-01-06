from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from fastapi import HTTPException

from app.models import User
from app.schemas import UserIn, UserUpdate
from app.core import get_password_hash


async def create_user(session: AsyncSession, user: UserIn):
    user_db = User(username=user.username, email=user.email.lower(), hashed_password=get_password_hash(user.password))

    try:
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return user_db

    except IntegrityError as e:
        await session.rollback()

        if "uq_user_username" in str(e):
            raise HTTPException(status_code=409, detail="Username already exists")

        if "uq_user_email" in str(e):
            raise HTTPException(status_code=409, detail="Email already exists")

        raise HTTPException(status_code=409, detail="Integrity error in creating user")
    
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Error in creating user")

async def get_user_by_email(session: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    return result.scalars().first()

async def set_login_date_now(session: AsyncSession, email: str):
    try:
        stmt = (
            update(User)
            .where(User.email == email)
            .values(last_login=func.now())
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()

    except Exception:
        await session.rollback()
        return None
    
async def set_verified_true(session: AsyncSession, email: str):
    try:
        stmt = (
            update(User)
            .where(User.email == email)
            .values(is_verified = True)
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception:
        await session.rollback()
        return None
    
async def update_user_data(session: AsyncSession, email: str, user_update: UserUpdate):
    values_to_update = user_update.model_dump(exclude_unset=True)
    if not values_to_update:
         return await get_user_by_email(session, email)
    stmt = update(User).where(User.email == email).values(**values_to_update).returning(User)
    try:
        result = await session.execute(stmt)
        updated_user = result.scalars().first()
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        await session.commit()
        return updated_user
    except IntegrityError as e:
        await session.rollback()

        if "uq_user_username" in str(e):
            raise HTTPException(status_code=409, detail="Username already exists")
        
        raise HTTPException(status_code=409, detail="Integrity error in creating user")
    
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_profile_image_path(session: AsyncSession, email: str, image_path: str):
    try:
        stmt = (
            update(User)
            .where(User.email == email)
            .values(profile_image=image_path)
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()

    except Exception:
        await session.rollback()
        return None
    
async def delete_profile_image_path(session: AsyncSession, email: str):
    try:
        stmt = (
            update(User)
            .where(User.email == email)
            .values(profile_image=None)
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()

    except Exception:
        await session.rollback()
        return None
    
async def update_user_password(session: AsyncSession, email:str, password: str):
    try:
        stmt = (
            update(User)
            .where(User.email == email)
            .values(hashed_password=get_password_hash(password))
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()

    except Exception:
        await session.rollback()
        return None