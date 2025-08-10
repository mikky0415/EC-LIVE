from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"].startswith("EC-LIVE")

def test_health_initial():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["phase"] == "phase1"
    assert "config" in data and "connection" in data

def test_config_and_test():
    r = client.post("/config", json={"api_base_url": "https://example.com", "api_key": "abcd1234xyz"})
    assert r.status_code == 200
    cfg = r.json()["config"]
    assert cfg["api_base_url"] == "https://example.com"
    assert cfg["api_key_set"] is True

    r2 = client.get("/api/test")
    assert r2.status_code == 200
    res = r2.json()["result"]
    assert res["configured"] is True
