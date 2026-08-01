
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.helper_functions import (
    generate_access_token,
    generate_refresh_token,
    get_client_ip,
)
from config.settings import settings
from models.auth import User
from models.refresh_token import RefreshToken
from services.mail_service import send_login_alert_email, send_welcome_email


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def _build_token_response(user: User) -> dict:
    return {
        "access_token": generate_access_token(user.id, user.email),
        "refresh_token": generate_refresh_token(user.id, user.email),
        "token_type": "bearer",
    }


async def register_user_service(data, background_tasks: BackgroundTasks, db: AsyncSession):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await db.execute(select(User).where(User.username == data.username))
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    try:
        new_user = User(
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip() if data.last_name else None,
            username=data.username.strip().lower(),
            email=data.email.strip().lower(),
            password=_hash_password(data.password),
            avatar=data.avatar,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

    background_tasks.add_task(send_welcome_email, new_user.email, new_user.username)
    tokens = _build_token_response(new_user)
    await save_refresh_token(new_user.id, tokens["refresh_token"], db)
    return tokens



async def login_service(request, data, background_tasks: BackgroundTasks, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email.strip().lower()))
    user = result.scalar_one_or_none()

    # same error for both "user not found" and "wrong password" — prevents user enumeration
    if not user or not _verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    from datetime import datetime, timezone
    ip = get_client_ip(request)
    login_time = datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p UTC")
    background_tasks.add_task(send_login_alert_email, user.email, user.username, login_time, ip)

    tokens = _build_token_response(user)
    await save_refresh_token(user.id, tokens["refresh_token"], db)
    return tokens


async def update_profile_service(user_id: int, data, db: AsyncSession):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.first_name is not None:
        user.first_name = data.first_name.strip()
    if data.last_name is not None:
        user.last_name = data.last_name.strip()
    if data.avatar is not None:
        user.avatar = data.avatar

    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Profile update failed")

    return user


async def generate_otp_service(email: str, redis_client) -> str:
    await redis_client.delete(f"otp:{email}")
    otp = str(secrets.randbelow(1000000)).zfill(6)
    await redis_client.setex(f"otp:{email}", 600, otp)
    return otp


async def verify_otp_service(data, redis_client) -> bool:
    stored_otp = await redis_client.get(f"otp:{data.email}")

    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP expired or not requested")

    if stored_otp != str(data.otp):
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    await redis_client.delete(f"otp:{data.email}")
    # mark email as OTP-verified for 5 minutes — reset password must happen within this window
    await redis_client.setex(f"otp_verified:{data.email}", 300, "true")
    return True


async def reset_password_service(data, redis_client, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email.strip().lower()))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    is_verified = await redis_client.get(f"otp_verified:{data.email}")
    if not is_verified:
        raise HTTPException(status_code=403, detail="OTP verification required before reset")

    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        user.password = _hash_password(data.new_password)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Password reset failed")

    await redis_client.delete(f"otp_verified:{data.email}")
    return {"message": "Password reset successfully"}


async def save_refresh_token(user_id: int, refresh_token: str, db: AsyncSession) -> None:
    payload = jwt.decode(refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=["HS256"])
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

    await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))

    new_token = RefreshToken(
        token=refresh_token,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(new_token)
    await db.commit()


async def logout_service(
    access_token: str,
    refresh_token: str,
    redis_client,
    db: AsyncSession,
) -> None:
    try:
        payload = jwt.decode(
            access_token,
            settings.ACCESS_TOKEN_SECRET,
            algorithms=["HS256"]
        )
        exp = payload.get("exp")
        if exp:
            ttl = int(exp - datetime.now(timezone.utc).timestamp())
            if ttl > 0:
                await redis_client.setex(f"blacklist:{access_token}", ttl, "true")
    except jwt.InvalidTokenError:
        pass

    await db.execute(
        delete(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    await db.commit()


async def refresh_access_token_service(
    refresh_token: str,
    redis_client,
    db: AsyncSession,
) -> dict:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired, please login again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked, please login again")

    user_id = payload.get("user_id")
    email = payload.get("email")

    from config.helper_functions import generate_access_token
    new_access_token = generate_access_token(user_id, email)

    return {"access_token": new_access_token, "token_type": "bearer"}

