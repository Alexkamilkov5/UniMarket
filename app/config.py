import os
from typing import Final

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Секретный ключ для подписи JWT
SECRET_KEY: Final[str] = os.getenv("UNIMARKET_SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("UNIMARKET_SECRET_KEY is not set! Add it to your .env file.")

# Алгоритм шифрования
ALGORITHM: Final[str] = os.getenv("JWT_ALGORITHM", "HS256")

# Время жизни токена (в минутах)
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
