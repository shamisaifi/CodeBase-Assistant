from fastapi import APIRouter, Depends, Response
from schemas.auth import UserCreate, UserResponse, LoginRequest, TokenResponse, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_user
from services.auth_service import login_service, register_user_serive, update_profile_service
from models.auth import User

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await register_user_serive(data, db)
    return result

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await login_service(data, db)
    return result

@router.get("/user_profile", response_model=UserResponse)
async def user_profile(current_user: User = Depends(get_current_user)):
    return current_user
    

@router.put("/update-profile")
async def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = update_profile_service(current_user.id, data, db)
    return result

@router.post("reset-password")
async def reset_password():
    pass
