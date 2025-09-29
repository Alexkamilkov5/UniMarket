from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_version_ok() -> None:
    r = client.get("/version")
    assert r.status_code == 200
    assert r.json() == {"version": "0.1.0"}
