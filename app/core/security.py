from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone

from typing import Any
from fastapi import HTTPException

from app.config import settings


pwd_context = CryptContext(
    schemes=['bcrypt'], 
    deprecated='auto'
)

def get_password_hash(password: str) -> str:
    """
    Hashes a password for storing.

    Args:
        password (str): The password to hash.

    Returns:
        str: A hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against a hashed password.

    Args:
        plain_password (str): The password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: Whether the password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict[str, Any], expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_delta if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict[str, Any], expires_delta: int | None = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(tz=timezone.utc) + timedelta(days=expires_delta if expires_delta else settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expires, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_verify_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    payload: dict[str, Any] = {
        "sub": email,
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def get_email_by_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True}  # default True
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")
        return email

    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token invalid")