import random

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login():
    userNik = "Alice" + str(random.randint(1, 10000))
    # регистрация — JSON
    r = client.post("/auth/register", json={"username": userNik, "password": "secret"})
    assert r.status_code == 200

    # логин — ФОРМА (а не json!)
    r2 = client.post(
        "/auth/login", data={"username": userNik, "password": "secret"}  # <-- важно
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert "access_token" in data2
    assert data2["token_type"] == "bearer"
