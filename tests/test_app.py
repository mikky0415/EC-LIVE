from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch, MagicMock
import os

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


def test_items_endpoint_missing_token():
    """Test GET /items returns 500 when BASE_ACCESS_TOKEN is not set"""
    # Ensure BASE_ACCESS_TOKEN is not set
    with patch.dict(os.environ, {}, clear=True):
        response = client.get('/items')
        assert response.status_code == 500
        data = response.json()
        assert 'detail' in data
        assert 'BASE_ACCESS_TOKEN' in data['detail']


@patch('app.routers.items.requests.get')
def test_items_endpoint_success(mock_get):
    """Test GET /items success path with mocked upstream response"""
    # Mock successful upstream response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"id": 1, "name": "Test Item 1", "price": 100},
            {"id": 2, "name": "Test Item 2", "price": 200}
        ],
        "total": 2
    }
    mock_get.return_value = mock_response
    
    # Set environment variables
    with patch.dict(os.environ, {
        'BASE_API_URL': 'https://api.base.ec',
        'BASE_ACCESS_TOKEN': 'test-token-123'
    }):
        response = client.get('/items?limit=10&visible=true')
        
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert len(data['items']) == 2
        assert data['total'] == 2
        
        # Verify the upstream API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        
        # Check URL (first positional argument)
        assert call_args[0][0] == 'https://api.base.ec/1/items'
        
        # Check headers (keyword argument)
        headers = call_args[1]['headers']
        assert headers['Authorization'] == 'Bearer test-token-123'
        
        # Check query parameters were passed through
        params = call_args[1]['params']
        assert params['limit'] == 10
        assert params['visible'] == 'true'


@patch('app.routers.items.requests.get')
def test_items_endpoint_upstream_error(mock_get):
    """Test GET /items handles upstream errors properly"""
    # Mock upstream error response (e.g., 401 Unauthorized)
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        "error": "Unauthorized",
        "message": "Invalid access token"
    }
    mock_get.return_value = mock_response
    
    # Set environment variables
    with patch.dict(os.environ, {
        'BASE_API_URL': 'https://api.base.ec',
        'BASE_ACCESS_TOKEN': 'invalid-token'
    }):
        response = client.get('/items')
        
        # Should return the upstream error with same status code
        assert response.status_code == 401
        data = response.json()
        assert 'error' in data
        assert data['error'] == 'Unauthorized'


@patch('app.routers.items.requests.get')
def test_items_endpoint_timeout_error(mock_get):
    """Test GET /items handles timeout errors"""
    # Mock timeout exception
    from requests.exceptions import Timeout
    mock_get.side_effect = Timeout("Request timed out")
    
    # Set environment variables
    with patch.dict(os.environ, {
        'BASE_API_URL': 'https://api.base.ec',
        'BASE_ACCESS_TOKEN': 'test-token'
    }):
        response = client.get('/items')
        
        assert response.status_code == 504
        data = response.json()
        assert 'detail' in data
        assert 'timed out' in data['detail']


@patch('app.routers.items.requests.get')
def test_items_endpoint_connection_error(mock_get):
    """Test GET /items handles connection errors"""
    # Mock connection exception
    from requests.exceptions import ConnectionError
    mock_get.side_effect = ConnectionError("Unable to connect")
    
    # Set environment variables
    with patch.dict(os.environ, {
        'BASE_API_URL': 'https://api.base.ec',
        'BASE_ACCESS_TOKEN': 'test-token'
    }):
        response = client.get('/items')
        
        assert response.status_code == 502
        data = response.json()
        assert 'detail' in data
        assert 'connect' in data['detail']