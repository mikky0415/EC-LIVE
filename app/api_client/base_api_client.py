import requests

class BaseAPIClient:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def get(self, endpoint):
        response = requests.get(f'{self.api_url}/{endpoint}', headers={'Authorization': f'Bearer {self.api_key}'})
        return response.json()
