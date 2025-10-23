import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

# Загружаем переменные из .env
DATABASE_URL: Final[str] = os.getenv("DATABASE_URL", "sqlite:///./unimarket.db")
SECRET_KEY: Final[str] = os.getenv("UNIMARKET_SECRET_KEY", "dev-secret-change-me")
ALGORITHM: Final[str] = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)
