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
