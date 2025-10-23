# tests/conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ВАЖНО: установить тестовый URL ДО импорта app.main
os.environ["DATABASE_URL"] = "sqlite:///./unimarket.db"

from app.database import Base
from app.main import app, get_db

# Один engine для всех тестов
engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _prepare_db():
    # Раз в сессию создаём таблицы
    Base.metadata.create_all(bind=engine)
    yield
    # В конце сессии — удаляем
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    # Перед каждым тестом — чистим таблицы (чтобы не текли данные)
    # В SQLite быстрее дроп/криэйт:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Подмена зависимости приложения
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
