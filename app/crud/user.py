from sqlalchemy import update, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from fastapi import HTTPException
from typing import Any
from datetime import datetime, timezone, timedelta

from app.models import User
from app.schemas import UserIn, UserUpdate, UserUpdateAdmin
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
    
async def get_all_users(session: AsyncSession, limit: int = 1000, skip: int = 0):
    stmt = select(User).limit(limit).offset(skip)
    result = await session.execute(stmt)
    return result.scalars().all()

async def get_user_by_id(session: AsyncSession, id: int):
    stmt = select(User).where(User.id == id)
    result = await session.execute(stmt)
    return result.scalars().first()

async def delete_user_by_id(session: AsyncSession, id: int):
    stmt = delete(User).where(User.id == id)
    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def ban_user_by_id(session: AsyncSession, id: int):
    stmt = update(User).where(User.id == id).values(is_active = False).returning(User)

    try:
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Iternal server error")
    
async def unban_user_by_id(session: AsyncSession, id: int):
    stmt = update(User).where(User.id == id).values(is_active = True).returning(User)

    try:
        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()
    except Exception:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Iternal server error")
    
async def update_user_data_admin(session: AsyncSession, id: int, update_user: UserUpdateAdmin):
    values_to_update = update_user.model_dump(exclude_unset=True)
    if not values_to_update:
        return await get_user_by_id(session, id)
    
    stmt = update(User).where(User.id == id).values(**values_to_update).returning(User)
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

async def get_user_statistics(session: AsyncSession) -> dict[str, Any]:

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    today_start = datetime(now.year, now.month, now.day)

    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    total_users = await session.scalar(select(func.count()).select_from(User)) or 0
    active_users = await session.scalar(select(func.count()).where(User.is_active == True)) or 0
    verified_users = await session.scalar(select(func.count()).where(User.is_verified == True)) or 0
    superusers = await session.scalar(select(func.count()).where(User.is_superuser == True)) or 0

    reg_today = await session.scalar(
        select(func.count()).where(User.created_at >= today_start)
    )
    reg_last_7 = await session.scalar(
        select(func.count()).where(User.created_at >= last_7_days)
    )
    reg_last_30 = await session.scalar(
        select(func.count()).where(User.created_at >= last_30_days)
    )

    logged_today = await session.scalar(
        select(func.count()).where(User.last_login >= today_start)
    )
    logged_last_7 = await session.scalar(
        select(func.count()).where(User.last_login >= last_7_days)
    )
    logged_last_30 = await session.scalar(
        select(func.count()).where(User.last_login >= last_30_days)
    )
    never_logged_in = await session.scalar(
        select(func.count()).where(User.last_login == None)
    )

    timezone_rows = await session.execute(
        select(User.timezone, func.count()).group_by(User.timezone)
    )
    timezones = {tz or "Unknown": count for tz, count in timezone_rows.all()}

    with_profile = await session.scalar(
        select(func.count()).where(User.profile_image.isnot(None))
    ) or 0

    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "superusers": superusers
        },

        "registrations": {
            "today": reg_today,
            "last_7_days": reg_last_7,
            "last_30_days": reg_last_30
        },

        "activity": {
            "logged_today": logged_today,
            "logged_last_7_days": logged_last_7,
            "logged_last_30_days": logged_last_30,
            "never_logged_in": never_logged_in
        },

        "timezones": timezones,

        "profile": {
            "with_profile_image": with_profile,
            "without_profile_image": total_users - with_profile
        }
    }

async def update_profile_image_path_by_id(session: AsyncSession, id: int, image_path: str):
    try:
        stmt = (
            update(User)
            .where(User.id == id)
            .values(profile_image=image_path)
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()

    except Exception:
        await session.rollback()
        return None
    
async def delete_profile_image_path_by_id(session: AsyncSession, id: int):
    try:
        stmt = (
            update(User)
            .where(User.id == id)
            .values(profile_image=None)
            .returning(User)
        )

        result = await session.execute(stmt)
        await session.commit()
        return result.scalars().first()

    except Exception:
        await session.rollback()
        return None