from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login():
    # регистрация — JSON
    r = client.post("/auth/register", json={"username": "bob8", "password": "secret"})
    assert r.status_code == 200

    # логин — ФОРМА (а не json!)
    r2 = client.post(
        "/auth/login", data={"username": "bob8", "password": "secret"}  # <-- важно
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert "access_token" in data2
    assert data2["token_type"] == "bearer"
