from fastapi import APIRouter, Depends, HTTPException, Path, Body

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.crud import get_all_categories, create_category, get_category, update_category, delete_category, get_all_tasks_by_category, get_category_statistics
from app.schemas import CategoryOut, CategoryIn, CategoryUpdate, TaskOut


router = APIRouter(
    prefix="/categories",
    tags=["Category"]
)

@router.get("/", response_model=list[CategoryOut])
async def get_user_categories(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    categories = await get_all_categories(session, user)
    if not categories:
        raise HTTPException(status_code=404, detail="You do not have any categories.")
    return categories

@router.post("/", response_model=CategoryOut)
async def add_categories(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    category: Annotated[CategoryIn, CategoryIn]
):
    category_db = await create_category(session, user, category)
    return category_db

@router.get("/statistics")
async def get_category_statistics_of_user(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    return await get_category_statistics(session, user)

@router.get("/{category_id}", response_model=CategoryOut)
async def get_category_by_id(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    category_id: Annotated[int, Path()]
):
    category = await get_category(session, user, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category

@router.put("/{category_id}", response_model=CategoryOut)
async def category_update_by_id(
    category_id: Annotated[int, Path()],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
    category_update: Annotated[CategoryUpdate, Body()]
):
    updated_category = await update_category(session, category_id, user, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found.")
    return updated_category

@router.delete("/{category_id}")
async def category_delete_by_id(
    category_id: Annotated[int, Path()],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    await delete_category(session, category_id, user)
    return {"message": "Category deleted."}

@router.get("/{category_id}/tasks", response_model=list[TaskOut])
async def get_tasks_by_category_id(
    category_id: Annotated[int, Path()],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    return await get_all_tasks_by_category(session, category_id, user)
