from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to the API'}

def test_read_root_japanese():
    response = client.get('/japanese')
    assert response.status_code == 200
    assert response.json() == {'message': 'APIへようこそ'}

def test_ai_model_info():
    response = client.get('/ai-model')
    assert response.status_code == 200
    data = response.json()
    assert '私はChatGPT-5' in data['message']
    assert data['ai_model'] == 'Advanced AI Assistant with ChatGPT-5 capabilities'
    assert 'Japanese' in data['language_support']
    assert data['response_in_japanese'] == True
