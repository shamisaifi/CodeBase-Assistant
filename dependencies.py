from collections.abc import AsyncGenerator

import jwt
import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from db.session import SessionLocal
from models.auth import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
    request: Request = None,
) -> User:
    token = credentials.credentials

    if request and hasattr(request.app.state, "redis"):
        is_blacklisted = await request.app.state.redis.get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        payload = jwt.decode(token, settings.ACCESS_TOKEN_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return user



async def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis
