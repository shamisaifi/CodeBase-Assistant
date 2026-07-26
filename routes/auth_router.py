import os
from typing import Annotated

import redis.asyncio as redis
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.helper_functions import get_client_ip
from config.settings import settings
from dependencies import get_current_user, get_db, get_redis
from models.auth import User
from schemas.auth import (
    LoginRequest,
    ResetPassword,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
    VerifyEmail,
    VerifyOtp,
)
from services.auth_service import (
    generate_otp_service,
    login_service,
    register_user_service,
    reset_password_service,
    update_profile_service,
    verify_otp_service,
)
from services.mail_service import send_otp_email, send_password_reset_success_email
from services.upload_service import (
    save_to_cloudinaryk,
    save_to_disk,
    validate_image_service,
)

router = APIRouter()

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
RedisClient = Annotated[redis.Redis, Depends(get_redis)]



@router.post("/register", response_model=TokenResponse)
async def register(
    data: UserCreate, 
    background_tasks: BackgroundTasks,
    db: DBSession
    ):
    result = await register_user_service(data, background_tasks, db)
    return result



@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest, 
    background_tasks: BackgroundTasks,
    db: DBSession
    ):
    
    result = await login_service(request, data, background_tasks, db)
    return result



@router.get("/user_profile", response_model=UserResponse)
async def user_profile(
    current_user: CurrentUser
    ):
    return current_user
    


@router.put("/update-profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate, 
    current_user: CurrentUser, 
    db: DBSession
    ):
    result = await update_profile_service(current_user.id, data, db)
    return result



@router.post("/send-otp")
async def send_otp(
    data: VerifyEmail,
    background_tasks: BackgroundTasks,
    redis_client: RedisClient, 
    db: DBSession
    ):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found, Enter a valid email")
    
    otp = await generate_otp_service(user.email, redis_client)
    background_tasks.add_task(send_otp_email, user.email, otp, user.username)

    return {"status": 200, "message": "OTP sent successfully"}



# Verify OTP
@router.post("/verify-otp")
async def verify_otp(
    data: VerifyOtp, 
    redis_client: RedisClient
    ):
    is_otp_correct = await verify_otp_service(data, redis_client)

    if not is_otp_correct:
        raise HTTPException(status_code=403, detail="wrong otp")

    return {"message": "OTP verified successfully"}



@router.post("/reset-password")
async def reset_password(
    request: Request,
    data: ResetPassword,
    background_tasks: BackgroundTasks,
    redis_client: RedisClient,
    db: DBSession
):
    result = await reset_password_service(data, redis_client, db)
    
    ip = get_client_ip(request)
    background_tasks.add_task(
        send_password_reset_success_email,
        data.email,
        ip
    )
    return result


@router.post("/upload-avatar", response_model=UserResponse)
async def upload_avatar(
    current_user: CurrentUser,
    db: DBSession,
    file: UploadFile = File(...)
):
    validate_image_service(file)

    if current_user.avatar and os.path.exists(current_user.avatar):
        os.remove(current_user.avatar)

    if settings.STORAGE == "local":
        file_path = await save_to_disk(file, "uploads/avatar")
    elif settings.STORAGE == "cloudinary":
        file_path = await save_to_cloudinaryk(file)
    
    current_user.avatar = file_path

    await db.commit()
    await db.refresh(current_user)
    return current_user

