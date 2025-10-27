# test_config.py
"""
Скрипт для проверки конфигурации
"""
from app.config import settings

print("=== Проверка конфигурации ===\n")

print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
print(f"VERSION: {settings.VERSION}")
print(f"DEBUG: {settings.DEBUG} (тип: {type(settings.DEBUG).__name__})")
print(f"PORT: {settings.PORT} (тип: {type(settings.PORT).__name__})")
print(f"DATABASE_URL: {settings.DATABASE_URL}")
# print(f"SECRET_KEY: {'*' * len(settings.UNIMARKET_SECRET_KEY} #(скрыт)"}
print(f"ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")

print("\n✅ Конфигурация загружена успешно!")
