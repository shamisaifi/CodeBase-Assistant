from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: Optional[str] = None
    username: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)
    avatar: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: str
    email: EmailStr
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class VerifyEmail(BaseModel):
    email: EmailStr

class VerifyOtp(VerifyEmail):
    otp: str

class ResetPassword(VerifyEmail):
    new_password: str
    confirm_new_password: str