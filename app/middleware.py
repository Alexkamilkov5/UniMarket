import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import decode_token

logger = logging.getLogger("unimarket")  # Создаем логгер для приложения
logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования
handler = logging.FileHandler("logs/unimarket.log", encoding="utf-8")  # Логируем в файл
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)  # Форматируем сообщения логов
handler.setFormatter(formatter)  # Устанавливаем форматтер для обработчика
logger.addHandler(handler)  # Добавляем обработчик к логгеру


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()  # Засекаем время начала обработки запроса
        client_ip = (
            request.client.host if request.client else "unknown"
        )  # Получаем IP клиента
        # client_ip = request.headers.get("x-forwarded-for", request.client.host) # Получаем IP
        # Если   Nginx или Traefik — этот заголовок обязательно проксироваться, иначе127.0.0.1.
        user_agent = request.headers.get("user-agent", "unknown")  # Получаем User-Agent
        # Извлекаем токен, если есть
        auth_header = request.headers.get(
            "authorization"
        )  # Получаем заголовок авторизации
        username = "anonymous"
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]  # Извлекаем токен из заголовка
            try:
                payload = decode_token(token)
                username = payload.get(
                    "sub", "unknown"
                )  # Извлекаем имя пользователя из полезной нагрузки токена
            except Exception:
                username = "invalid_token"

        logger.info(
            f"🌐 IP: {client_ip} | 🧍‍♂️ User: {username} | "
            f"👤 User: {username} | Method: {request.method} | Path: {request.url.path}"
            f"User-Agent: {user_agent}"
        )

        # response = await call_next(request)
        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"❌ Ошибка при обработке запроса: {e}")
            raise e

        duration = round(
            time.time() - start_time, 3
        )  # Вычисляем длительность обработки запроса
        logger.info(
            f"✅ Completed {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration}s)"
        )

        return response
