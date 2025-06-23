from pydantic import BaseModel, EmailStr
from models.user import UserRole

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    role: UserRole

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class Message(BaseModel):
    message: str

class RoleUpdate(BaseModel):
    role: str

class Config:
    orm_mode = True