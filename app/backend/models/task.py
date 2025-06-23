from enum import Enum
from typing import Optional, Dict
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr

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