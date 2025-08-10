import os
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_items_requires_token(monkeypatch):
    monkeypatch.delenv("BASE_ACCESS_TOKEN", raising=False)
    resp = client.get("/items")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "BASE_ACCESS_TOKEN is not set"


def test_items_ok(monkeypatch):
    # Arrange environment
    monkeypatch.setenv("BASE_ACCESS_TOKEN", "token")
    monkeypatch.setenv("BASE_API_URL", "https://api.base.ec")

    # Mock requests.get
    class DummyResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def json(self):
            return {"items": [], "count": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        assert url == "https://api.base.ec/1/items"
        assert headers["Authorization"].startswith("Bearer ")
        return DummyResp()

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    # Act
    resp = client.get("/items?limit=3")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "count" in data
