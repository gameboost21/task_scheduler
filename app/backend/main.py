from enum import Enum

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, create_engine, Session, Field, select
from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv('DATABASE_URL')



class Run(Enum):
    LOCAL = "local"
    REMOTE = "remote"

class Task(SQLModel, table=True):
    id: int | None = Field(primary_key=True, index=True)
    taskname: str
    sheduled: bool
    runcount: int
    successful: bool


app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

#Creating a Task:
@app.post("/tasks/", response_model=Task)
def create_task(task:Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

#Get Tasks
@app.get("/tasks/", response_model=list[Task])
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
       
