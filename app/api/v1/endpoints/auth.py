from fastapi import APIRouter, Depends, Response, HTTPException, Cookie, Request, Query, Body, UploadFile, File
from fastapi.responses import FileResponse

from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
import shutil

from app.schemas import UserIn, UserLogIn, UserOutResponse, UserOut, UserUpdate
from app.database import get_db
from app.models import User
from app.crud import create_user, get_user_by_email, set_login_date_now, set_verified_true, update_user_data, update_profile_image_path, delete_profile_image_path
from app.services import save_refresh_token, get_user_email_by_refresh_token, delete_refresh_token
from app.core import verify_password, create_access_token, create_refresh_token, create_verify_token, get_email_by_token
from app.tasks import send_verify_email_task
from app.config import settings
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

MEDIA_ROOT = Path("media/profile_images")

@router.post("/register", response_model=UserOutResponse)
async def register_user(
    user: Annotated[UserIn, Body()],
    session: Annotated[AsyncSession, Depends(get_db)],
    request: Request
) -> dict[str, Any]:
    token = create_verify_token(user.email)
    user_db = await create_user(session, user)
    verification_url = request.url_for("verify-email").include_query_params(token=token)
    send_verify_email_task.delay(user_db.email, str(verification_url)) # type: ignore
    return {
        "status": "ok",
        "message": "User created",
        "user": user_db
    }

@router.post("/verify-email", name="verify-email", response_model=UserOutResponse)
async def verify_email(
    token: Annotated[str, Query()],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    email: str = get_email_by_token(token)
    user = await get_user_by_email(session, email)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    if user.is_verified:
        raise HTTPException(status_code=409, detail="User is already verified")
    user: User | None = await set_verified_true(session, email)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid token")
    return {
        "status": "ok",
        "message": "Email verified",
        "user": user
    }

@router.post("/login")
async def login_user(
    user: Annotated[UserLogIn, UserLogIn],
    session: Annotated[AsyncSession, Depends(get_db)],
    response: Annotated[Response, Response]
):
    user_db = await get_user_by_email(session, user.email)

    if not user_db or not verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user_db.is_active:
        raise HTTPException(status_code=400, detail="User is not active")

    # if not user_db.is_verified:
    #     raise Response(status_code=400, content="User is not verified")

    await set_login_date_now(session, user_db.email)

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    await save_refresh_token(refresh_token, user_db.email)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_user(
    response: Annotated[Response, Response],
    refresh_token: Annotated[str | None, Cookie] = None
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not provided")
    
    email = await get_user_email_by_refresh_token(refresh_token)

    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    await delete_refresh_token(refresh_token)

    new_access = create_access_token({"sub": email})
    new_refresh = create_refresh_token({"sub": email})

    await save_refresh_token(new_refresh, email)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
    )

    return {"access_token": new_access, "token_type": "bearer"}

@router.post("/logout")
async def logout_user(
    response: Annotated[Response, Response],
    refresh_token: Annotated[str | None, Cookie] = None
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not provided")

    email = get_user_email_by_refresh_token(refresh_token)

    email = await get_user_email_by_refresh_token(refresh_token)
    if email:
        await delete_refresh_token(refresh_token)
    response.delete_cookie("refresh_token", samesite="lax")
    return {
        "status": "ok",
        "detail": "Successfully logged out"
    }

@router.get("/me", response_model=UserOut)
async def get_me(user: Annotated[User, Depends(get_current_user)]):
    return user

@router.put("/me", response_model=UserOutResponse)
async def update_user(
    user: Annotated[User, Depends(get_current_user)],
    user_update: Annotated[UserUpdate, Body()],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    updated_user = await update_user_data(session, user.email, user_update)
    return {
        "status": "ok",
        "message": "User updated",
        "user": updated_user
    }

@router.post("me/profile-image", response_model=UserOutResponse)
async def update_profile_image(
    file: Annotated[UploadFile, File(...)],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    user_folder = MEDIA_ROOT / str(user.id)
    user_folder.mkdir(parents=True, exist_ok=True)

    profile_path = user_folder / "profile.png"
    if profile_path.exists():
        profile_path.unlink()
    
    with profile_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    user_updated = await update_profile_image_path(session, user.email, str(profile_path))

    return {
        "status": "ok",
        "message": "Profile image updated",
        "user": user_updated
    }

@router.get("me/profile-image")
async def get_profile_image(
    user: Annotated[User, Depends(get_current_user)]
):
    if not user.profile_image:
        raise HTTPException(status_code=404, detail="Profile image not found")
    
    image_path = Path(user.profile_image)
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Profile image file not found")
    
    return FileResponse(image_path)

@router.delete("me/profile-image", response_model=UserOutResponse)
async def delete_profile_image(
    user: Annotated[User, Depends(get_current_user)], 
    session: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    if not user.profile_image:
        raise HTTPException(status_code=404, detail="You do not have profile image")
    
    image_path = Path(user.profile_image)
    if image_path.exists():
        image_path.unlink()
    
    user_updated = await delete_profile_image_path(session, user.email)
    
    return {
        "status": "ok",
        "message": "Profile image has been deleted",
        "user": user_updated
    }