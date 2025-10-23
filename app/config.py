# src/config.py
"""
Конфигурация приложения UniMarket через Pydantic Settings
"""
# from typing import Optional

import os

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения.
    Значения читаются из переменных окружения или .env файла.
    """

    # === Основные настройки ===
    PROJECT_NAME: str = "UniMarket"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # === API настройки ===
    API_PREFIX: str = "/api/v1"
    HOST: str = os.getenv("HOST", "127.0.0.1")  # По умолчанию localhost
    PORT: int = int(os.getenv("PORT", "8000"))

    # === База данных ===
    DATABASE_URL: str = "sqlite:///./unimarket.db"

    # === Безопасность ===
    UNIMARKET_SECRET_KEY: str = "vrem-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # === CORS (для фронтенда) ===
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Конфигурация Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=".env",  # Читать из .env файла
        env_file_encoding="utf-8",  # Кодировка файла
        case_sensitive=True,  # Учитывать регистр
        extra="ignore",  # Игнорировать лишние переменные
    )

    def is_development(self) -> bool:
        """Проверка, что запущено в режиме разработки"""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Проверка, что запущено в production"""
        return self.ENVIRONMENT == "production"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Валидация SECRET_KEY:
        - Минимум 32 символа
        - Не должен быть дефолтным значением
        """
        if len(v) < 32:
            raise ValueError("SECRET_KEY должен быть минимум 32 символа")

        forbidden = ["change-me", "secret", "password", "dev-secret"]
        if any(word in v.lower() for word in forbidden):
            raise ValueError(
                "SECRET_KEY содержит небезопасное значение. "
                "Сгенерируйте случайную строку!"
            )

        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Валидация URL базы данных"""
        valid_prefixes = ["sqlite://", "postgresql://", "mysql://"]

        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                f"DATABASE_URL должен начинаться с одного из: {valid_prefixes}"
            )

        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """
        Проверка настроек для production окружения
        """
        if self.is_production():
            # В production DEBUG должен быть False
            if self.DEBUG:
                raise ValueError("DEBUG должен быть False в production!")

            # В production не должно быть sqlite
            if "sqlite" in self.DATABASE_URL:
                raise ValueError("Используйте PostgreSQL в production!")

        return self


# Создаем глобальный экземпляр настроек
settings = Settings()


# Функция для получения настроек (для Depends в FastAPI)
def get_settings() -> Settings:
    """
    Фабрика для создания настроек с учетом окружения.
    Читает переменную ENV для выбора файла конфигурации.
    """
    env = os.getenv("ENV", "development")
    env_file = f".env.{env}"

    # Проверяем существование файла
    if not os.path.exists(env_file):
        print(f"⚠️  Файл {env_file} не найден, используется .env")
        env_file = ".env"

    class DynamicSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=env_file,  # ← Переопределяем файл
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
        )

    return DynamicSettings()


# Глобальный экземпляр
settings = get_settings()
