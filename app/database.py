from __future__ import annotations

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DB_URL = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "sqlite:///./unimarket.db"

if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

# engine = create_engine(DB_URL, pool_pre_ping=True, connect_args=connect_args)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)
Base = declarative_base()
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
