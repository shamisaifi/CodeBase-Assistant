from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from schemas.auth import UserCreate, UserResponse, LoginRequest, TokenResponse, UserUpdate, VerifyEmail, VerifyOtp, ResetPassword
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from dependencies import get_db, get_current_user, get_redis
from services.auth_service import login_service, register_user_service, update_profile_service, generate_otp_service, verify_otp_service, reset_password_service
from services.mail_service import send_otp_email
from models.auth import User

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await register_user_service(data, db)
    return result

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await login_service(data, db)
    return result

@router.get("/user_profile", response_model=UserResponse)
async def user_profile(current_user: User = Depends(get_current_user)):
    return current_user
    

@router.put("/update-profile", response_model=UserResponse)
async def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await update_profile_service(current_user.id, data, db)
    return result

@router.post("/send-otp")
async def send_otp(
    data: VerifyEmail,
    Background_tasks = Depends(BackgroundTasks),
    redis: redis.Redis = Depends(get_redis), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found, Enter a valid email")
    
    otp = await generate_otp_service(user.email, redis)
    Background_tasks.add_task(send_otp_email, user.email, otp, user.username)

    return {"status": 200, "message": "OTP sent successfully"}

# Verify OTP
@router.post("/verify-otp")
async def very_otp(data: VerifyOtp, redis: redis.Redis = Depends(get_redis)):
    is_otp_correct = await verify_otp_service(data, redis)

    if not is_otp_correct:
        raise HTTPException(status_code=403, detail="wrong otp")

    return {"message": "OTP verified successfully"}

@router.post("/reset-password")
async def reset_password(
    data: ResetPassword, 
    redis: redis.Redis = Depends(get_redis), 
    db: AsyncSession = Depends(get_db)
):
    result = await reset_password_service(data, redis, db)
