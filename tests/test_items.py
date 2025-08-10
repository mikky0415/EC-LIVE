import os
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestItemsEndpoint:
    """Test cases for GET /items endpoint"""
    
    def test_items_missing_token(self):
        """Test that missing BASE_ACCESS_TOKEN returns 500 with helpful message"""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure BASE_ACCESS_TOKEN is not set
            if 'BASE_ACCESS_TOKEN' in os.environ:
                del os.environ['BASE_ACCESS_TOKEN']
            
            response = client.get('/items')
            assert response.status_code == 500
            data = response.json()
            assert 'detail' in data
            assert 'BASE_ACCESS_TOKEN' in data['detail']
    
    @patch('app.routers.items.requests.get')
    def test_items_success(self, mock_get):
        """Test successful request to items endpoint with mocked upstream response"""
        # Mock successful response from BASE API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": 1, "name": "Test Item 1", "price": 100},
                {"id": 2, "name": "Test Item 2", "price": 200}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'BASE_ACCESS_TOKEN': 'test-token'}):
            response = client.get('/items')
            
            assert response.status_code == 200
            data = response.json()
            assert 'items' in data
            assert len(data['items']) == 2
            assert data['total'] == 2
            
            # Verify that requests.get was called with correct parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == 'https://api.base.ec/1/items'  # URL
            assert call_args[1]['headers']['Authorization'] == 'Bearer test-token'
            assert call_args[1]['timeout'] == 30
    
    @patch('app.routers.items.requests.get')
    def test_items_with_query_params(self, mock_get):
        """Test that query parameters are passed through to BASE API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'BASE_ACCESS_TOKEN': 'test-token'}):
            response = client.get('/items', params={
                'visible': 'true',
                'order': 'asc',
                'sort': 'name',
                'limit': 10,
                'offset': 0,
                'category_id': 'cat123',
                'max_image_no': 5,
                'image_size': 'large'
            })
            
            assert response.status_code == 200
            
            # Verify query parameters were passed through
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]['params']
            assert params['visible'] == 'true'
            assert params['order'] == 'asc'
            assert params['sort'] == 'name'
            assert params['limit'] == 10
            assert params['offset'] == 0
            assert params['category_id'] == 'cat123'
            assert params['max_image_no'] == 5
            assert params['image_size'] == 'large'
    
    @patch('app.routers.items.requests.get')
    def test_items_upstream_error_with_json(self, mock_get):
        """Test upstream error with JSON response is returned properly"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "Invalid token",
            "code": "UNAUTHORIZED"
        }
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'BASE_ACCESS_TOKEN': 'invalid-token'}):
            response = client.get('/items')
            
            assert response.status_code == 401
            data = response.json()
            assert data['error'] == 'Invalid token'
            assert data['code'] == 'UNAUTHORIZED'
    
    @patch('app.routers.items.requests.get')
    def test_items_upstream_error_non_json(self, mock_get):
        """Test upstream error with non-JSON response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_get.return_value = mock_response
        
        with patch.dict(os.environ, {'BASE_ACCESS_TOKEN': 'test-token'}):
            response = client.get('/items')
            
            assert response.status_code == 500
            data = response.json()
            assert 'error' in data
            assert 'Upstream API returned non-JSON response' in data['error']
            assert data['status_code'] == 500
    
    @patch('app.routers.items.requests.get')
    def test_items_timeout_error(self, mock_get):
        """Test timeout error handling"""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Request timed out")
        
        with patch.dict(os.environ, {'BASE_ACCESS_TOKEN': 'test-token'}):
            response = client.get('/items')
            
            assert response.status_code == 504
            data = response.json()
            assert 'timed out' in data['detail'].lower()
    
    @patch('app.routers.items.requests.get')
    def test_items_connection_error(self, mock_get):
        """Test connection error handling"""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        with patch.dict(os.environ, {'BASE_ACCESS_TOKEN': 'test-token'}):
            response = client.get('/items')
            
            assert response.status_code == 502
            data = response.json()
            assert 'connect' in data['detail'].lower()
    
    def test_items_custom_base_url(self):
        """Test that custom BASE_API_URL is used when set"""
        with patch('app.routers.items.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": []}
            mock_get.return_value = mock_response
            
            with patch.dict(os.environ, {
                'BASE_ACCESS_TOKEN': 'test-token',
                'BASE_API_URL': 'https://custom-api.example.com'
            }):
                response = client.get('/items')
                
                assert response.status_code == 200
                
                # Verify custom URL was used
                mock_get.assert_called_once()
                call_args = mock_get.call_args
                assert call_args[0][0] == 'https://custom-api.example.com/1/items'