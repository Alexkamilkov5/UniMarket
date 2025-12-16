import argparse
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app directory to path so we can import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.auth import hash_password  # noqa: E402
from app.models import User  # noqa: E402

load_dotenv()

DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "sqlite:///./unimarket.db"
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_admin(username, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User {username} found. Promoting to admin...")
            user.role = "admin"
            if password:
                print("Updating password...")
                user.hashed_password = hash_password(password)
        else:
            print(f"User {username} not found. Creating new admin...")
            if not password:
                print("Error: Password required for new user.")
                return
            user = User(
                username=username, hashed_password=hash_password(password), role="admin"
            )
            db.add(user)

        db.commit()
        print(f"Successfully configured {username} as admin.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or promote an admin user.")
    parser.add_argument("username", help="Username for the admin")
    parser.add_argument(
        "password", nargs="?", help="Password (optional if promoting existing user)"
    )

    args = parser.parse_args()
    create_admin(args.username, args.password)
