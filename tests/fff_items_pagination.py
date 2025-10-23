# import random

# import pytest
# from fastapi.testclient import TestClient

# from app.main import app  # или откуда импортируется ваше приложение
# from tests.conftest import client  # noqa: F401

# @pytest.fixture
# def client():
#     return TestClient(app)


def test_items_pagination_and_sort(client):
    # подготовка данных
    # (если фикстуры уже создают что-то — можно очистить/пересоздать БД)
    for i in range(1, 16):
        client.post("/items", json={"name": f"Item{i}", "price": i * 10})

    # первая страница 10 элементов
    r1 = client.get("/items?limit=10&offset=0")
    assert r1.status_code == 200
    page1 = r1.json()
    assert page1["limit"] == 3
    assert page1["offset"] == 0
    assert page1["total"] >= 15
    assert len(page1["items"]) == 3
    assert page1["next_offset"] == 10

    # вторая страница
    r2 = client.get("/items?limit=10&offset=10")
    assert r2.status_code == 200
    page2 = r2.json()
    # на второй странице останется >=5 элементов
    assert len(page2["items"]) >= 5
    # сортировка по цене по убыванию
    r3 = client.get("/items?limit=5&offset=0&sort_by=price&order=desc")
    assert r3.status_code == 200
    page3 = r3.json()
    prices = [it["price"] for it in page3["items"]]
    assert prices == sorted(prices, reverse=True)
