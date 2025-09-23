from itertools import count
from typing import Dict

from fastapi import FastAPI, HTTPException, Query, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field

app = FastAPI(title="UniMarket", version="0.1.0")

# =========================
# МОДЕЛИ (Pydantic)
# =========================


class HelloResponse(BaseModel):
    message: str = Field(..., examples=["Hello, Alice!"])


class RegisterRequest(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$"
    )
    password: str = Field(..., min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    username: str


class UserDB(BaseModel):
    id: int
    username: str
    hashed_password: str


# =========================
# «БД» В ПАМЯТИ + ХЕШИРОВАНИЕ
# =========================

users_db: Dict[str, UserDB] = {}  # ключ: username
_id_seq = count(start=1)  # генератор ID

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


# =========================
# ЭНДПОИНТЫ
# =========================


@app.get("/health")  # type: ignore[misc]
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/hello", response_model=HelloResponse)  # type: ignore[misc]
def hello(name: str = Query("world")) -> HelloResponse:
    return HelloResponse(message=f"Hello, {name}!")


@app.post(
    "/auth/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)  # type: ignore[misc]
def register(payload: RegisterRequest) -> UserPublic:
    """
    Регистрирует нового пользователя:
    - проверяет уникальность username,
    - хеширует пароль (bcrypt),
    - сохраняет в «БД» в памяти,
    - возвращает публичные данные (без пароля).
    """
    username = payload.username.strip()

    if username in users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )

    uid = next(_id_seq)
    user = UserDB(
        id=uid, username=username, hashed_password=hash_password(payload.password)
    )
    users_db[username] = user
    return UserPublic(id=user.id, username=user.username)
