import pytest
from app.api_client.base_api_client import BaseAPIClient


def test_get_mocks_requests(monkeypatch):
    # Arrange
    client = BaseAPIClient("https://api.example.com", "key")

    class DummyResp:
        def json(self):
            return {"ok": True}

    def fake_get(url, headers=None):
        assert url == "https://api.example.com/test-endpoint"
        assert headers and "Authorization" in headers
        return DummyResp()

    import requests

    monkeypatch.setattr(requests, "get", fake_get)

    # Act
    response = client.get("test-endpoint")

    # Assert
    assert response == {"ok": True}
