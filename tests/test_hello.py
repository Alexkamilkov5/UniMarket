from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello_default() -> None:
    r = client.get("/hello")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, world!"}


def test_hello_named() -> None:
    r = client.get("/hello?name=Alice")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, Alice!"}
