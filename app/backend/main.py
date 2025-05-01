from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel


class Run(Enum):
    LOCAL = "local"
    REMOTE = "remote"
class Task(BaseModel):
    type: str
    sheduled: bool
    runcount: int
    successful: bool
    run: Run


app = FastAPI()

tasks = {
    
    0: Task(type="OS", sheduled="True", runcount="4", successful="True", run=Run.LOCAL),
    1: Task(type="OS", sheduled="False", runcount="3", successful="False", run=Run.REMOTE),
    2: Task(type="Bash", sheduled="True", runcount="1", successful="False", run=Run.LOCAL)

}

@app.get("/")
def index() -> dict[str, dict[int, Task]]:
    return {"tasks" : tasks}

@app.get("/tasks/{task_id}")
def query_task_by_id(task_id: int) -> Task:
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found."
        )
    return tasks[task_id]

#@app.post()
#def creat_task():

#@app.delete()
#def remove_task():
