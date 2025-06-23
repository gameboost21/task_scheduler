from enum import Enum
from typing import Optional, Dict
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr

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

