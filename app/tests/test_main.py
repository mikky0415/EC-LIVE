from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get('/')
    assert response.status_code == 200
    message = response.json()['message']
    assert message.startswith('EC-LIVE'), f"Expected message to start with 'EC-LIVE', got: {message}"


def test_oauth_callback_success():
    resp = client.get('/callback?code=abc123&state=xyz')
    assert resp.status_code == 200
    data = resp.json()
    assert data['received'] is True
    assert data['code'] == 'abc123'
    assert data['state'] == 'xyz'


def test_oauth_callback_missing_code():
    resp = client.get('/callback')
    assert resp.status_code == 400
    assert resp.json()['detail'] == "Missing 'code' query parameter"
