from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from schemas.user import Message, UserRead, RoleUpdate
from db.session import get_session
from core.security import require_admin
from models.user import Users, UserRole

router = APIRouter()

@router.post("/admin/approve/{user_id}", response_model=Message)
def approve_user(user_id: int, session: Session = Depends(get_session), user: Users = Depends(require_admin)):
    
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message" : f"User {user.username} has been approved and activated."}



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
    