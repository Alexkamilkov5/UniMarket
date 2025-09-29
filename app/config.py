import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()  # подхватит .env локально, если есть

SECRET_KEY: Final[str] = os.getenv("UNIMARKET_SECRET_KEY", "dev-secret-change-me")
ALGORITHM: Final[str] = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
