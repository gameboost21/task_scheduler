from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session, Field, select
from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv('DATABASE_URL')



class Run(Enum):
    LOCAL = "local"
    REMOTE = "remote"

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    taskname: str
    sheduled: bool
    runcount: int
    successful: bool


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


def get_session():
    with Session(engine) as session:
        yield session

#Creating a Task:
@app.post("/tasks", response_model=Task)
def create_task(task:Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

#Get Tasks
@app.get("/tasks", response_model=list[Task])
def get_tasks(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    query = select(Task).offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks

#Get Task by ID:
@app.get("/tasks/{task_id}", response_model=Task)
def get_task_by_id(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    return task

#Update Task:
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: Task, session: Session = Depends(get_session)):
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
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not f0und")
    
    session.delete(task)
    session.commit()
    return task
       
