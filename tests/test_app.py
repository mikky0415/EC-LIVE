from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test GET / returns JSON with message starting with 'EC-LIVE'"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.json()
    assert 'message' in data
    assert data['message'].startswith('EC-LIVE'), f"Expected message to start with 'EC-LIVE', got: {data['message']}"

def test_health_endpoint():
    """Test GET /health returns JSON with phase, config, and connection"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert 'phase' in data
    assert data['phase'] == 'phase1'
    
    assert 'config' in data
    assert 'connection' in data
    
    # Config should contain info about API configuration
    config = data['config']
    assert 'api_base_url_set' in config
    assert 'api_key_set' in config

def test_post_config():
    """Test POST /config accepts JSON with api_base_url and api_key, returns masked config"""
    config_data = {
        "api_base_url": "https://test-api.example.com",
        "api_key": "test-api-key-123"
    }
    
    response = client.post('/config', json=config_data)
    assert response.status_code == 200
    data = response.json()
    
    assert 'config' in data
    config = data['config']
    
    # Check that api_base_url is stored and returned
    assert config['api_base_url'] == config_data['api_base_url']
    
    # Check that api_key is masked (not directly exposed)
    assert 'api_key' not in config
    assert config['api_key_set'] == True

def test_api_test_endpoint():
    """Test GET /api/test returns result of client test_connection()"""
    response = client.get('/api/test')
    assert response.status_code == 200
    data = response.json()
    
    assert 'result' in data
    result = data['result']
    
    # Should contain connection test results
    assert 'configured' in result

def test_config_flow():
    """Test full flow: configure API, then check that configured flag is true"""
    # First, configure the API
    config_data = {
        "api_base_url": "https://configured-api.example.com",
        "api_key": "configured-key-456"
    }
    
    config_response = client.post('/config', json=config_data)
    assert config_response.status_code == 200
    
    # Check that configuration is set
    test_response = client.get('/api/test')
    assert test_response.status_code == 200
    test_data = test_response.json()
    
    # After POST /config both base_url and api_key are set, configured flag should be true
    result = test_data['result']
    assert result['configured'] == True
    assert result['base_url'] == config_data['api_base_url']
    assert result['api_key_set'] == True