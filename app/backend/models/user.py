from enum import Enum
from typing import Optional, Dict
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta

class UserRole(str, Enum):
    admin = "admin"
    moderator = "moderator"
    power_user = "power_user"
    viewer = "viewer"

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    hashed_password: str
    is_active: bool = False
    is_admin: bool = False
    role: UserRole = Field(default=UserRole.viewer)

class UserApprovalToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    token: str = Field(nullable=False, unique=True)

