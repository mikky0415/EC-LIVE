# Configuration for the API client
import os

API_URL = 'https://api.example.com'
API_KEY = 'your_api_key'


class RuntimeConfig:
    """Runtime configuration for API client"""
    
    def __init__(self):
        self.api_base_url = None
        self.api_key = None
        # Read BASE API configuration from environment variables
        self.base_api_url = os.getenv('BASE_API_URL', 'https://api.base.ec')
        self.base_access_token = os.getenv('BASE_ACCESS_TOKEN')
    
    def masked(self):
        """Return configuration with sensitive data masked"""
        return {
            "api_base_url": self.api_base_url,
            "api_key_set": bool(self.api_key)
        }
