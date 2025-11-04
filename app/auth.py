# Additional code for JWT token creation
from datetime import datetime, timedelta, timezone
from typing import Optional, cast

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

SECRET_KEY = settings.UNIMARKET_SECRET_KEY
ALGORITHM = settings.ALGORITHM
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
)
# современный идентификатор
# bcrypt__truncate_error=False  # по умолчанию False, оставляю явно на случай


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))
