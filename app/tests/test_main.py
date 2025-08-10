from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get('/')
    assert response.status_code == 200
    message = response.json()['message']
    assert message.startswith('EC-LIVE'), f"Expected message to start with 'EC-LIVE', got: {message}"
