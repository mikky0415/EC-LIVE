import os
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_exchange_uses_basic_auth(monkeypatch):
    # Arrange env
    monkeypatch.setenv("BASE_CLIENT_ID", "cid")
    monkeypatch.setenv("BASE_CLIENT_SECRET", "sec")
    monkeypatch.setenv("BASE_OAUTH_TOKEN_URL", "https://api.base.ec/1/oauth/token")

    class DummyResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def json(self):
            return {"access_token": "at", "refresh_token": "rt"}

    def fake_post(url, data=None, headers=None, auth=None, timeout=None):
        assert url.endswith("/1/oauth/token")
        assert data["grant_type"] == "authorization_code"
        assert data["code"] == "abc"
        # Basic auth used
        assert auth == ("cid", "sec")
        return DummyResp()

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    resp = client.post("/auth/exchange", json={"code": "abc", "use_basic_auth": True})
    assert resp.status_code == 200
    assert resp.json()["access_token"] == "at"


def test_exchange_missing_creds(monkeypatch):
    monkeypatch.delenv("BASE_CLIENT_ID", raising=False)
    monkeypatch.delenv("BASE_CLIENT_SECRET", raising=False)
    resp = client.post("/auth/exchange", json={"code": "abc"})
    assert resp.status_code == 500
    assert resp.json()["detail"] == "BASE_CLIENT_ID/BASE_CLIENT_SECRET is not set"


def test_refresh_ok_with_basic_auth(monkeypatch):
    # Arrange env
    monkeypatch.setenv("BASE_CLIENT_ID", "cid")
    monkeypatch.setenv("BASE_CLIENT_SECRET", "sec")
    monkeypatch.setenv("BASE_OAUTH_TOKEN_URL", "https://api.base.ec/1/oauth/token")

    class DummyResp:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def json(self):
            return {"access_token": "new_at", "refresh_token": "new_rt"}

    def fake_post(url, data=None, headers=None, auth=None, timeout=None):
        assert url.endswith("/1/oauth/token")
        assert data["grant_type"] == "refresh_token"
        assert data["refresh_token"] == "rt"
        assert auth == ("cid", "sec")
        return DummyResp()

    import requests
    monkeypatch.setattr(requests, "post", fake_post)

    resp = client.post("/auth/refresh", json={"refresh_token": "rt", "use_basic_auth": True})
    assert resp.status_code == 200
    assert resp.json()["access_token"] == "new_at"


def test_refresh_missing_refresh_token(monkeypatch):
    monkeypatch.setenv("BASE_CLIENT_ID", "cid")
    monkeypatch.setenv("BASE_CLIENT_SECRET", "sec")
    monkeypatch.delenv("BASE_REFRESH_TOKEN", raising=False)
    resp = client.post("/auth/refresh", json={})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Missing 'refresh_token'"
