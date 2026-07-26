import secrets
from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException
from sqlalchemy import select

from config.helper_functions import (
    generateAccessToken,
    generateRefreshToken,
    get_client_ip,
)
from models.auth import User
from services.mail_service import send_login_alert_email, send_welcome_email


# Registration
async def register_user_service(data, background_tasks, db):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=400, detail="User already exist")
    
    password_bytes = data.password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt )
    password_hash = password_hash.decode('utf-8')

    new_user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        email=data.email,
        password=password_hash,
        avatar=data.avatar
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    payload = {"user_id": new_user.id, "email": new_user.email}
    access_token = generateAccessToken(payload)
    refresh_token = generateRefreshToken(payload)

    background_tasks.add_task(send_welcome_email, new_user.email, new_user.username)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# Login
async def login_service(request, data, background_tasks, db):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    is_correct = bcrypt.checkpw(data.password.encode(), user.password.encode())
    if not is_correct:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"user_id": user.id, "email": user.email}
    access_token = generateAccessToken(payload)
    refresh_token = generateRefreshToken(payload)

    ip = get_client_ip(request)
    time = datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p UTC")
    background_tasks.add_task(send_login_alert_email, user.email, time, ip)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# Update Profile
async def update_profile_service(user_id, data, db):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.first_name = data.first_name if data.first_name is not None else user.first_name
    user.last_name = data.last_name if data.last_name is not None else user.last_name
    user.avatar = data.avatar if data.avatar is not None else user.avatar

    await db.commit() 
    await db.refresh(user)
    return user


# Generate OTP
async def generate_otp_service(email, redis_client):
    stored_otp = await redis_client.get(f"otp:{email}")
    if stored_otp:
        await redis_client.delete(f"otp:{email}")
    
    new_otp = str(secrets.randbelow(1000000)).zfill(6)
    await redis_client.setex(f"otp:{email}", 600, new_otp)
    return new_otp


# Verify OTP
async def verify_otp_service(data, redis_client):
    stored_otp = await redis_client.get(f"otp:{data.email}")
    
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP expired or not requested")
    
    if stored_otp != data.otp:
        raise HTTPException(status_code=400, detail="Wrong OTP")
    
    await redis_client.setex(f"otp_verified:{data.email}", 300, "true")
    await redis_client.delete(f"otp:{data.email}")

    return True


# Reset Password
async def reset_password_service(data, redis_client, db):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid email id")

    is_verified = await redis_client.get(f"otp_verified:{data.email}")
    if not is_verified:
        raise HTTPException(status_code=403, detail="OTP not verified")
    await redis_client.delete(f"otp_verified:{data.email}")

    new_pass = data.new_password
    confirm_new_pass = data.confirm_new_password

    if new_pass != confirm_new_pass:
        raise HTTPException(status_code=400, detail="Password do not match")

    new_pass_bytes = new_pass.encode('utf-8')
    salt = bcrypt.gensalt()
    new_hashed_pass = bcrypt.hashpw(new_pass_bytes, salt)
    new_hashed_pass = new_hashed_pass.decode('utf-8')

    user.password = new_hashed_pass
    await db.commit()
    await db.refresh(user)

    return {"message": "Password reset successfully"}
