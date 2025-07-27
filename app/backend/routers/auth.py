"""
auth.py

This module defines authentication-related endpoints for a FastAPI application. It includes functionality for user login, registration, and password change.

Dependencies:
- FastAPI: Used for creating API endpoints.
- SQLModel: Used for database interactions.
- Core modules: Security, email handling, and session management.
- Models and schemas: Define the structure of user data.

Environment Variables:
- ACCESS_TOKEN_EXPIRE_MINUTES: Specifies the expiration time for access tokens.

Endpoints:
1. /login
   - Authenticates a user and generates an access token.
2. /register
   - Registers a new user and sends a notification email to admin users.
3. /change-password
   - Allows a user to change their password.
"""

from core.security import OAuth2PasswordRequestForm, verify_password, create_access_token, hash_password
from fastapi import FastAPI, APIRouter, HTTPException, Depends, BackgroundTasks
from sqlmodel import select, Session
from models.user import Users
from schemas.user import Message, UserCreate, PasswordChangeRequest
from db.session import get_session
from core.security import require_viewer
from core.email import send_email
import os
from dotenv import load_dotenv

# Initialize the router for authentication-related endpoints
router = APIRouter()

# Load environment variable for token expiration
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")

# Login endpoint
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Authenticates a user and generates an access token.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): Contains username and password.
    - session (Session): Database session dependency.

    Returns:
    - dict: Access token and token type.

    Raises:
    - HTTPException: Incorrect username/password or inactive account.
    """
    user = session.exec(select(Users).where(Users.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect Username or Password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account not approved by admin")

    access_token = create_access_token(user=user, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access_token, "token_type": "bearer"}

# Registration endpoint
@router.post("/register", response_model=Message)
def register(user: UserCreate, background_task: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Registers a new user and sends a notification email to admin users.

    Parameters:
    - user (UserCreate): Contains user registration details.
    - background_task (BackgroundTasks): Used for sending emails asynchronously.
    - session (Session): Database session dependency.

    Returns:
    - dict: Success message.

    Raises:
    - HTTPException: Username already exists.
    """
    admin_users = session.exec(
        select(Users).where(Users.role == "admin", Users.email != None)
    ).all()

    admin_emails = [admin.email for admin in admin_users if admin.email]
    
    existing = session.exec(select(Users).where(Users.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = hash_password(user.password)

    new_user = Users(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        is_active=False,
        is_admin=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    background_task.add_task(send_email, new_user, admin_emails)

    return {"message": "Registration request submitted. Awaiting Admin approval"}

# Change password endpoint
@router.post("/change-password", response_model=Message)
def change_password(data: PasswordChangeRequest, session: Session = Depends(get_session), user: Users = Depends(require_viewer)):
    """
    Allows a user to change their password.

    Parameters:
    - data (PasswordChangeRequest): Contains old and new passwords.
    - session (Session): Database session dependency.
    - user (Users): Authenticated user dependency.

    Returns:
    - dict: Success message.

    Raises:
    - HTTPException: Old password is incorrect.
    """
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Old password is incorrect")
    
    user.hashed_password = hash_password(data.new_password)
    session.add(user)
    session.commit()
    return {"message": "Password changed successfully"}