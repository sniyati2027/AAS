from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.models.user import UserRole, UserStatus


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    status: UserStatus
    is_active: bool
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    class Config:
        from_attributes = True


class UserApprovalRequest(BaseModel):
    reason: Optional[str] = None
