# 🛒 UniMarket API

**Описание:** мини-маркетплейс на FastAPI с регистрацией, логином и добавлением товаров.

## 🚀 Установка
```bash
git clone https://github.com/Alexkamilkov5/UniMarket.git
cd UniMarket
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

Документация API: http://localhost:8000/docs

Соберите и запушьте образ в реестр (пример):
docker build -t your-registry/unimarket:latest .
docker push your-registry/unimarket:latest
Запуск (на продакшн-хосте):
docker compose -f docker-compose.prod.yml up -d
Выполнить миграции (если нужно):
docker compose -f docker-compose.prod.yml run --rm migrate
Логи/статус:
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
