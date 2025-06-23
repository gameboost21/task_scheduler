from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt

from sqlmodel import Session, select

from models.user import Users, UserRole
from db.session import get_session

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_unsafe_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")

bcrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plaintext: str, hashed: str) -> bool:
    return bcrypt.verify(plaintext, hashed)

def create_access_token(user: Users, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "is_active": user.is_active,
        "exp": datetime.now() + (expires_delta or timedelta(minutes=15))
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.get(Users, int(user_id))
    if user is None:
        raise credentials_exception
    return user

def require_role(required_roles = list[UserRole]):
    def role_checker(user: Users = Depends(get_current_user)):
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Not authorized for this action")
        return user
    return role_checker

require_admin = require_role([UserRole.admin])
require_moderator = require_role([UserRole.admin, UserRole.moderator])
require_power_user = require_role([UserRole.admin, UserRole.moderator, UserRole.power_user])
require_viewer = require_role([UserRole.admin, UserRole.moderator, UserRole.power_user, UserRole.viewer])