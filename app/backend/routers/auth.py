from core.security import OAuth2PasswordRequestForm, verify_password, create_access_token, hash_password
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlmodel import select, Session
from models.user import Users
from schemas.user import Message, UserCreate, PasswordChangeRequest
from db.session import get_session
from core.security import require_viewer
from core.email import send_email
import os
from dotenv import load_dotenv

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")

#Login endpoint
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(Users).where(Users.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect Username or Password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account not approved by admin")

    access_token = create_access_token(user=user, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token":access_token, "token_type":"bearer"}

#Registration endpoint
@router.post("/register", response_model=Message)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(Users).where(Users.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = hash_password(user.password)

    new_user = Users(
        username = user.username,
        email = user.email,
        hashed_password=hashed_pw,
        is_active=False,
        is_admin=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    send_email(
        subject = "New User awaiting approval",
        body = f"User '{user.username}' registered and is awaiting approval",
        to = os.getenv("ADMIN_EMAIL")
    )

    return {"message": "Registration request submitted. Awaiting Admin approval"}

@router.post("/change-password", response_model=Message)
def change_password(data: PasswordChangeRequest, session: Session = Depends(get_session), user: Users = Depends(require_viewer)):
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Old password is incorrect")
    
    user.hashed_password = hash_password(data.new_password)
    session.add(user)
    session.commit()
    return {"message" : "Password changed successfully"}