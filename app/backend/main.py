from fastapi import FastAPI
from sqlmodel import SQLModel
from fastapi.middleware.cors import CORSMiddleware

from routers import admin, auth, debug, tasks
from db.session import engine
from models.user import Users
from models.task import Task

#class Run(Enum):
#    LOCAL = "local"
#    REMOTE = "remote"

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

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(debug.router)
app.include_router(tasks.router)

SQLModel.metadata.create_all(engine)