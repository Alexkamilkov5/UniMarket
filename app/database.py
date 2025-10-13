from __future__ import annotations

import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
DB_URL = os.getenv("DB_URL", "sqlite:///./unimarket.db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./unimarket.db"
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


# Base = declarative_base()
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
