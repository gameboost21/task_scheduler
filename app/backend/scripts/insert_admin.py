import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, backend_dir)

from sqlmodel import Session, select
from ..db.session import engine
from ..models.user import Users, UserRole
from ..core.security import hash_password

def create_admin_user():
    with Session(engine) as session:
        existing = session.exec(select(Users).where(Users.username == "admin")).first()
        if existing:
            print("Admin user already exists")
        admin = Users(
            username= "admin",
            email="admin@example.com",
            hashed_password=hash_password("adminpass"),
            is_admin=True,
            is_active=True,
            role=UserRole.admin
        )
        session.add(admin)
        session.commit()
        print("Admin User created successfully")

if __name__ == "__main__":
    create_admin_user()