import random

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app  # или откуда импортируется ваше приложение
# from tests.conftest import client

# @pytest.fixture
# def client():
#     return TestClient(app)


def test_filter_items_by_category(client):
    # создаём две категории
    rand1 = str(random.randint(500, 5000))
    c1 = client.post("/categories", json={"name": "Ноутбуки" + rand1}).json()
    c2 = client.post("/categories", json={"name": "Телефоны" + rand1}).json()
    # товары в разных категориях
    client.post(
        "/items",
        json={"name": "Laptop" + rand1, "price": int(rand1), "category_id": c1["id"]},
    )
    client.post(
        "/items",
        json={"name": "iPhone" + rand1, "price": int(rand1), "category_id": c2["id"]},
    )

    r = client.get(f"/items?category_id={c1['id']}")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1 and data[0]["name"] == "Laptop" + rand1
