from sqlalchemy import and_, update, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException
from typing import Any

from app.models import User, Category, Task
from app.schemas import CategoryIn, CategoryUpdate, StatusEnum


async def get_all_categories(session: AsyncSession, user: User):
    stmt = select(Category).where(Category.user_id == user.id)
    result = await session.execute(stmt)
    return result.scalars().all()

async def create_category(session: AsyncSession, user: User, category: CategoryIn):
    category_db = Category(**category.model_dump(), user = user)

    try:
        session.add(category_db)
        await session.commit()
        await session.refresh(category_db)
        return category_db
    except IntegrityError as e:
        await session.rollback()

        if "uq_categories_user_name" in str(e):
            raise HTTPException(status_code=409, detail="You have already this category.")
        
        raise HTTPException(status_code=409, detail="Integrity error in creating category.")
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def get_category(session: AsyncSession, user: User, category_id: int):
    stmt = select(Category).where(and_(Category.id == category_id, Category.user_id == user.id))
    result = await session.execute(stmt)
    return result.scalars().first()

async def update_category(session: AsyncSession, category_id: int, user: User, category_update: CategoryUpdate):
    update_data = category_update.model_dump(exclude_unset=True)
    if not update_data:
        return await get_category(session, user, category_id)
    stmt = update(Category).where(and_(Category.id == category_id, Category.user_id == user.id)).returning(Category)
    try:
        result = await session.execute(stmt)
        updated_category = result.scalars().all()
        if not updated_category:
            raise HTTPException(status_code=404, detail="Category not found.")
        await session.commit()
        return updated_category
    except IntegrityError as e:
        await session.rollback()

        if "uq_categories_user_name" in str(e):
            raise HTTPException(status_code=409, detail="You have already this category.")
        
        raise HTTPException(status_code=409, detail="Integrity error in updating category.")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
async def delete_category(session: AsyncSession, category_id: int, user: User):
    stmt = select(Category).where(and_(Category.id == category_id, Category.user_id == user.id))
    result = await session.execute(stmt)
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    try:
        await session.delete(category)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
async def get_all_tasks_by_category(session: AsyncSession, category_id: int, user: User):
    stmt = select(Task).where(and_(Task.category_id == category_id, Task.user_id == user.id))
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    if not tasks:
        raise HTTPException(status_code=404, detail="You do not have tasks with this category.")
    return tasks

async def get_category_statistics(
    session: AsyncSession,
    user: User
) -> dict[str, Any]:
    stmt = (
        select(
            Category.id.label("id"),
            Category.name.label("name"),
            Category.color,
            Category.icon,

            func.count(Task.id).label("total_tasks"),

            func.sum(
                case(
                    (Task.status == StatusEnum.completed, 1),
                    else_=0
                )
            ).label("completed_tasks"),

            func.sum(
                case(
                    (Task.status == StatusEnum.pending, 1),
                    else_=0
                )
            ).label("pending_tasks"),

            func.sum(
                case(
                    (Task.status == StatusEnum.in_progress, 1),
                    else_=0
                )
            ).label("in_progress_tasks"),
        )
        .outerjoin(
            Task,
            Task.category_id == Category.id
        )
        .where(Category.user_id == user.id)
        .group_by(Category.id)
        .order_by(Category.created_at)
    )

    result = await session.execute(stmt)
    rows = result.mappings().all()

    return {
        "total_categories": len(rows),
        "categories": [
            {
                "id": row["id"],
                "name": row["name"],
                "color": row["color"],
                "icon": row["icon"],
                "total_tasks": row["total_tasks"],
                "completed_tasks": row["completed_tasks"] or 0,
                "pending_tasks": row["pending_tasks"] or 0,
                "in_progress_tasks": row["in_progress_tasks"] or 0,
            }
            for row in rows
        ]
    }
