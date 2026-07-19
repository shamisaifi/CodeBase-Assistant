from models.auth import User
from fastapi import HTTPException
from sqlalchemy import select
from config.helper_functions import generateAccessToken, generateRefreshToken
import bcrypt


async def register_user_serive(data, db):
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

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

async def login_service(data, db):
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

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

async def update_profile_service(user_id, data, db):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.firt_name = data.first_name or user.first_name
    user.last_name = data.last_name or user.last_name
    user.avatar = data.avatar or user.avater

    await db.commit() 
    await db.refresh(user)
    return user

