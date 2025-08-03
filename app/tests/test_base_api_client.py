import pytest
from app.api_client.base_api_client import BaseAPIClient

API_URL = 'https://api.example.com'
API_KEY = 'your_api_key'

client = BaseAPIClient(API_URL, API_KEY)

def test_get():
    response = client.get('test-endpoint')
    assert response is not None
