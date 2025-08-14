import os
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_orders_requires_token(monkeypatch):
    monkeypatch.delenv("BASE_ACCESS_TOKEN", raising=False)
    resp = client.get("/orders")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "BASE_ACCESS_TOKEN is not set"


def test_orders_ok(monkeypatch):
    monkeypatch.setenv("BASE_ACCESS_TOKEN", "token")
    monkeypatch.setenv("BASE_API_URL", "https://api.base.ec")

    class DummyResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def json(self):
            return {"orders": [], "count": 0}

    def fake_get(url, headers=None, params=None, timeout=None):
        assert url == "https://api.base.ec/1/orders"
        assert headers["Authorization"].startswith("Bearer ")
        assert params.get("limit") == 5
        return DummyResp()

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    resp = client.get("/orders?limit=5")
    assert resp.status_code == 200
    assert resp.json()["count"] == 0


def test_order_detail_ok(monkeypatch):
    monkeypatch.setenv("BASE_ACCESS_TOKEN", "token")
    monkeypatch.setenv("BASE_API_URL", "https://api.base.ec")

    class DummyResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def json(self):
            return {"order": {"order_id": 123}}

    def fake_get(url, headers=None, params=None, timeout=None):
        assert url == "https://api.base.ec/1/orders/detail"
        assert params.get("order_id") == 123
        return DummyResp()

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    resp = client.get("/orders/detail?order_id=123")
    assert resp.status_code == 200
    assert resp.json()["order"]["order_id"] == 123
