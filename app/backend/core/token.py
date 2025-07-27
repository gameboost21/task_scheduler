from itsdangerous import URLSafeTimedSerializer
from typing import Optional
import os, secrets
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from sqlmodel import Session
from models.user import UserApprovalToken

SECRET = os.getenv("SECRET_KEY_TOKEN")
serializer = URLSafeTimedSerializer(SECRET)

def create_secure_token(session: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(32)  # Generate a secure random token
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    approval_token = UserApprovalToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )   
    session.add(approval_token)
    session.commit()
    return token  

def verify_secure_token(token: str) -> Optional[int]:
    try:
        return serializer.loads(token, salt="approve-user", max_age=3600)  # Token valid for 1 hour
    except Exception:
        return None