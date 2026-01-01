from fastapi import APIRouter, Depends, Response, HTTPException, Cookie

from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserIn, UserLogIn
from app.database import get_db
from app.crud import create_user, get_user_by_email, set_login_date_now
from app.services import save_refresh_token, get_user_email_by_refresh_token, delete_refresh_token
from app.core import verify_password, create_access_token, create_refresh_token

from app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register")
async def register_user(
    user: Annotated[UserIn, UserIn],
    session: Annotated[AsyncSession, Depends(get_db)]
):
    print(user.password)
    user_db = await create_user(session, user)
    return user_db

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