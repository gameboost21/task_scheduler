from enum import Enum
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException, Depends, APIRouter, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import SQLModel, create_engine, Session, Field, select, JSON
from dotenv import load_dotenv
import os, subprocess, logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
logging.getLogger('passlib').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

load_dotenv()

scheduler = BackgroundScheduler()
scheduler.start()

database_url = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_unsafe_key")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



class Run(Enum):
    LOCAL = "local"
    REMOTE = "remote"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    taskname: str
    sheduled: bool
    runcount: int
    successful: bool
    schedule_cron: Optional[str] = None
    script_path: Optional[str] = None
    parameters: Optional[str] = None
    script_type: str

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str

app = FastAPI()

origins = [
    "http://0.0.0.0:5173",
    "https://frontend.tuschkoreit.de",
    "http://127.24.0.7"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def run_script(task_id: int, script_path: str, parameters: str, script_type: str):
    try:
        if script_type == "python":
            command = ["python3", script_path]
        elif script_type == "bash":
            command = ["bash", script_path]
        else:
            logger.error(f"Unknown script type: {script_type}")
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

def get_session():
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(Users).where(Users.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

with Session(engine) as session:
    user = Users(username="testuser", hashed_password=pwd_context.hash("testpass"))
    session.add(user)
    session.commit()

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(Users).where(Users.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect Username or Password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token":access_token, "token_type":"bearer"}

#Creating a Task:
@app.post("/tasks", response_model=Task)
def create_task(task:Task, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
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
@app.get("/tasks", response_model=list[Task])
def get_tasks(user: Users = Depends(get_current_user), skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    query = select(Task).offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks

#Get Task by ID:
@app.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(task_id: int, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    return task

#Update Task:
@app.put("/tasks/{task_id}", response_model=Task)
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
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    
    session.delete(task)
    session.commit()
    return task
       
@app.get("/debug/jobs")
def list_jobs(user: Users = Depends(get_current_user)):
    return [str(job) for job in scheduler.get_jobs()]

@app.post("/debug/run-task/{task_id}")
def run_now(task_id: int, session: Session = Depends(get_session), user: Users = Depends(get_current_user)):
    task=session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    run_script(task.id, task.script_path, task.parameters or "")
    return {"status" : "task executed manually"}