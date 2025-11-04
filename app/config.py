# app/config.py
"""
Конфигурация приложения UniMarket через Pydantic Settings
"""

import os
from typing import Optional

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # === Основные настройки ===
    PROJECT_NAME: str = "UniMarket"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # === API настройки ===
    API_PREFIX: str = "/api/v1"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # === База данных ===
    DATABASE_URL: str = "sqlite:///./unimarket.db"

    # === Безопасность ===
    UNIMARKET_SECRET_KEY: str = (
        "GgCtQ-5lhnQ9xWTUrf3wGzht5Qu8TwiDk9hIY8z4_S107Xp3pzCmNWup1yrais"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === CORS (для фронтенда) ===
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Конфигурация pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ----- Утилиты -----
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    # ----- Валидаторы -----
    @field_validator("UNIMARKET_SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: Optional[str]) -> Optional[str]:
        """
        В development/test разрешаем пустой ключ (подставляем dev-значение).
        В production — требуем безопасный ключ (минимум 32 символа и не 'secret'/'change-me').
        """
        if v is None or v == "":
            # В dev/test возвращаем dev-значение вместо ошибки
            # Если хотите, можно поднять исключение в продакшне позднее.
            return "dev-secret-change-me"

        # Валидация только если явно задано значение
        if len(v) < 32:
            raise ValueError("UNIMARKET_SECRET_KEY должен быть минимум 32 символа")

        forbidden = ["change-me", "secret", "password", "dev-secret"]
        if any(word in v.lower() for word in forbidden):
            raise ValueError("UNIMARKET_SECRET_KEY содержит не значение.")

        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Простая проверка префикса DATABASE_URL.
        Дополнены варианты для psycopg/psycopg2.
        """
        valid_prefixes = [
            "sqlite://",
            "postgresql://",
            "postgresql+psycopg://",
            "postgresql+psycopg2://",
            "mysql://",
            "mysql+pymysql://",
        ]

        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                f"DATABASE_URL должен начинаться с одного из: {valid_prefixes}"
            )
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """
        Проверка настроек для production окружения.
        В production — запрещаем sqlite и DEBUG=True.
        """
        if self.is_production():
            if self.DEBUG:
                raise ValueError("DEBUG должен быть False в production!")
            if "sqlite" in (self.DATABASE_URL or ""):
                raise ValueError("Используйте PostgreSQL в production!")
        return self


# Фабрика: получаем настройки с учётом ENV (например .env.production)
def get_settings() -> Settings:
    env = os.getenv("ENV", "development")
    env_file = f".env.{env}"
    if not os.path.exists(env_file):
        # не аварийно — используем .env по умолчанию
        env_file = ".env"

    class DynamicSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=env_file,
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
        )

    return DynamicSettings()


# Глобальный экземпляр (создаётся ОДИН раз при импорте)
# Если вы хотите избежать валидации при unit-тестах, НЕ импортируйте settings в conftest.py
# или установите нужные env vars ДО импорта (см. tests/conftest.py пример).
settings = get_settings()
