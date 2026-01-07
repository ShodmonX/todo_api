from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.database import get_db
from app.crud import get_user_by_email
from app.config import settings


bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        type_ = payload.get("type")
        if not type_ or type_ != "access":
            raise HTTPException(status_code=400, detail="Invalid token")
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await get_user_by_email(db, email)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="You are banned, you cannot do this action.")

    return user

async def get_admin(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), 
):
    user = await get_current_user(db, credentials)
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="You are not a superuser.")
    return user