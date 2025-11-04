import random

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app  # или откуда импортируется ваше приложение
# from tests.conftest import client

# @pytest.fixture
# def client():
#     return TestClient(app)


def test_create_category(client):
    rand1 = random.randint(500, 5000)
    r = client.post("/categories", json={"name": "Ноутбуки" + str(rand1)})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Ноутбуки" + str(rand1)


def test_create_item_with_category(client):  # создаём категорию
    rand1 = random.randint(500, 5000)

    cat = client.post(
        "/categories", json={"name": "Телефоны" + str(rand1)}
    ).json()  # создаём товар
    r = client.post(
        "/items",
        json={
            "name": "iPhone" + str(rand1),
            "description": "13 Pro" + str(rand1),
            "price": rand1,
            "category_id": cat["id"],
        },
    )
    assert r.status_code == 200
    item = r.json()
    assert item["category_id"] == cat["id"]
