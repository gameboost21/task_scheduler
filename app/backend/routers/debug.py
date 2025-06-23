from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.session import get_session
from models.user import Users
from models.task import Task
from core.security import require_admin
from routers.tasks import run_script

router = APIRouter()

@router.post("/debug/run-task/{task_id}")
def run_now(task_id: int, session: Session = Depends(get_session), user: Users = Depends(require_admin)):
    task=session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    run_script(task.id, task.script_path, task.parameters or "")
    return {"status" : "task executed manually"}