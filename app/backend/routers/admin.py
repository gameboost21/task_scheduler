import logging
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from jinja2 import Environment, FileSystemLoader
from schemas.user import Message, UserRead, RoleUpdate
from db.session import get_session
from core.security import require_admin
from core.token import verify_secure_token
from models.user import Users, UserRole, UserApprovalToken
from core.email import send_approval_email

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates"))

@router.get("/admin/approve", response_class=HTMLResponse)
def approve_user(token: str, background_task: BackgroundTasks, request: Request, session: Session = Depends(get_session)):
    
    secure_token = session.exec(
        select(UserApprovalToken).where(UserApprovalToken.token == token)
    ).first()
    
    if not secure_token:
        return HTMLResponse("<h3>Invalid or expired token</h3>", status_code=403)

    if secure_token.expires_at < datetime.now(timezone.utc):
        return HTMLResponse("<h3>UToken has expires</h3>", status_code=404)
    
    target_user = session.get(Users, secure_token.user_id)
    if not target_user:
        return HTMLResponse("<h3>User not found</h3>", status_code=404)
    
    if not target_user.is_active:
        target_user.is_active = True
        target_user.role = UserRole.viewer  # Default role for approved users
        logger.info(f"Activating user {target_user.username} with role {target_user.role}")
        session.add(target_user)
        session.delete(secure_token)
        session.commit()
        session.refresh(target_user)
        logger.info(f"Approval email sent for {target_user.username}")
    else:
        logger.info(f"User {target_user.username} already active; skipping email.")

    background_task.add_task(send_approval_email, target_user)

    logged_in = "session" in request.cookies
    template = env.get_template("approve_success.html")
    html_content = template.render(logged_in=logged_in)
    return HTMLResponse(content=html_content)

    #return {"message" : f"User {target_user.username} has been approved and activated."}



@router.get("/admin/users", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session), _: Users = Depends(require_admin)):
    return session.exec(select(Users)).all()

@router.delete("/admin/users/{user_id}", response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session), user: Users = Depends(require_admin)):
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": f"User {user.username} deleted successfully"}

@router.put("/admin/users/{user_id}/role")
def update_user_role(user_id: int, payload: RoleUpdate, session: Session = Depends(get_session), _: Users = Depends(require_admin)):
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = payload.role
    session.add(user)
    session.commit()
    return {"message": f"User {user.id} has been modified successfully. Role now {user.role}"}
    