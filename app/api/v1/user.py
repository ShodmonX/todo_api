from fastapi import APIRouter, Depends, Query, Path, HTTPException, Body, UploadFile, File
from fastapi.responses import FileResponse

from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import shutil

from app.database import get_db
from app.schemas import UserOutAdmin, UserOutAdminResponse, UserUpdateAdmin
from app.dependencies import get_admin
from app.crud import get_all_users, get_user_by_id, delete_user_by_id, ban_user_by_id, unban_user_by_id, update_user_data_admin, get_user_statistics, update_profile_image_path_by_id, delete_profile_image_path_by_id


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_admin)]
)

MEDIA_ROOT = Path("media/profile_images")

@router.get("/", response_model=list[UserOutAdmin])
async def read_all_users(
    session: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query()] = 1000,
    skip: Annotated[int, Query()] = 0,
):
    return await get_all_users(session, limit, skip)

@router.get("/statistics")
async def get_statistics(session: Annotated[AsyncSession, Depends(get_db)]):
    return await get_user_statistics(session)

@router.get("/{user_id}", response_model=UserOutAdmin)
async def get_user_id(
    user_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    return await get_user_by_id(session, user_id)

@router.post("/{user_id}", response_model=UserOutAdminResponse)
async def update_user_id(
    user_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db)],
    user_update: Annotated[UserUpdateAdmin, Body()]
) -> dict[str, Any]:
    updated_user = await update_user_data_admin(session, user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "ok",
        "message": "User updated",
        "user": updated_user
    }

@router.delete("/{user_id}")
async def delete_user(
    user_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user_by_id(session, user_id)
    return {
        "status": "ok",
        "message": "User deleted"
    }

@router.post("/{user_id}/ban", response_model=UserOutAdminResponse)
async def ban_user(
    user_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    user = await ban_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "ok",
        "message": "User banned",
        "user": user
    }
    
@router.post("/{user_id}/unban", response_model=UserOutAdminResponse)
async def unban_user(
    user_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    user = await unban_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "ok",
        "message": "User unbanned",
        "user": user
    }

@router.post("/{user_id}/profile-image", response_model=UserOutAdminResponse)
async def update_profile_image(
    file: Annotated[UploadFile, File(...)],
    user_id: Annotated[int, Path()], 
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    user = await get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_folder = MEDIA_ROOT / str(user.id)
    user_folder.mkdir(parents=True, exist_ok=True)

    profile_path = user_folder / "profile.png"
    if profile_path.exists():
        profile_path.unlink()
    
    with profile_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    updated_user = await update_profile_image_path_by_id(session, user_id, "")

    return {
        "status": "ok",
        "message": "Profile image updated",
        "user": updated_user
    }

@router.get("/{user_id}/profile-image")
async def get_profile_image(
    user_id: Annotated[int, Path()], 
    session: Annotated[AsyncSession, Depends(get_db)]
):
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.profile_image:
        raise HTTPException(status_code=404, detail="Profile image not found")
    
    image_path = Path(user.profile_image)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Profile image file not found")
    
    return FileResponse(image_path)

@router.delete("/{user_id}/profile-image", response_model=UserOutAdminResponse)
async def delete_profile_image(
    user_id: Annotated[int, Path()], 
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    user = await get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.profile_image:
        raise HTTPException(status_code=404, detail="You do not have profile image")
    
    image_path = Path(user.profile_image)
    if image_path.exists():
        image_path.unlink()
    
    user_updated = await delete_profile_image_path_by_id(session, user_id)
    
    return {
        "status": "ok",
        "message": "Profile image deleted",
        "user": user_updated
    }
