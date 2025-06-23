from pydantic import BaseModel


class TaskCreate(BaseModel):
    taskname: str
    scheduled: bool = False
    script_path: str | None = None
    parameters: str | None = None
    script_type: str


class TaskRead(BaseModel):
    id: int
    taskname: str
    scheduled: bool
    runcount: int
    successful: bool
    script_path: str | None
    parameters: str | None
    script_type: str