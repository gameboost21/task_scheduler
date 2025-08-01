from sqlmodel import create_engine, Session, SQLModel
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session