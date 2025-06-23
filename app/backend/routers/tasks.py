from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from datetime import datetime, timedelta
from passlib.context import CryptContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess, logging

from db.session import get_session, engine
from models.task import Task
from models.user import Users
from core.security import get_current_user, require_viewer, require_moderator, require_power_user, require_admin


router = APIRouter()

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
logging.getLogger('passlib').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()

def run_script(task_id: int, script_path: str, parameters: str, script_type: str):
    try:
        if script_type == "python":
            command = ["python3", script_path]
        elif script_type == "bash":
            command = ["bash", script_path]
        else:
            logger.error(f"Unknown script type: {script_type}")
            raise HTTPException(status_code=404, detail=f"Script type {script_type} not found")
        if parameters:
            command += parameters.split()
        result = subprocess.run(command, check=True, capture_output=True)

        success = result.returncode == 0

        logger.info(f"Task {task_id} STDOUT:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Task {task_id} STDERR:\n{result.stderr}")

        with Session(engine) as session:
            task = session.exec(select(Task).where(Task.id == task_id)).first()
            if task:
                task.runcount += 1
                task.successful = success
                session.add(task)
                session.commit()
                logger.info(f"Task {task_id} updated in DB with runcount {task.runcount}, successful {task.successful}")

        print(f"Task {task_id} ran sucessfully.")
    except subprocess.CalledProcessError as e:
            logger.exception(f"Task {task_id} failed to execute: {e}")


#Creating a Task:
@router.post("/tasks", response_model=Task)
def create_task(task:Task, session: Session = Depends(get_session), user: Users = Depends(require_power_user)):
    session.add(task)
    session.commit()
    session.refresh(task)

    if task.sheduled and task.schedule_cron and task.script_path and task.script_type:
        trigger = CronTrigger.from_crontab(task.schedule_cron)
        scheduler.add_job(
            run_script,
            trigger,
            args=[task.id, task.script_path, task.parameters or "", task.script_type],
            id=str(task.id),
            replace_existing=True
        )

    return task

#Get Tasks
@router.get("/tasks", response_model=list[Task])
def get_tasks(user: Users = Depends(require_viewer), skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    query = select(Task).offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks

#Get Task by ID:
@router.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(task_id: int, session: Session = Depends(get_session), user: Users = Depends(require_viewer)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    return task

#Update Task:
@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: Task, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    #Get the task
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    #Update task
    for field, value in task_data.model_dump().items():
        setattr(task, field, value)

    session.commit()
    session.refresh(task)
    return task

#Delete Task
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session), user: Users = Depends(require_power_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    
    session.delete(task)
    session.commit()
    return task

@router.get("/debug/jobs")
def list_jobs(user: Users = Depends(require_admin)):
    return [str(job) for job in scheduler.get_jobs()]