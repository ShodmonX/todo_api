from redis.asyncio import Redis

from app.config import settings


redis = Redis(
    host='redis',
    decode_responses=True
)

async def save_refresh_token(token: str, email: str, expires_delta: int | None = None) -> None:
    await redis.set(f"refresh_token:{token}", email, ex=expires_delta if expires_delta else settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

async def get_user_email_by_refresh_token(token: str) -> str | None:
    return await redis.get(token)

async def delete_refresh_token(token: str) -> int:
    return await redis.delete(token)