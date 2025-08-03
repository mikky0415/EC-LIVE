from fastapi import FastAPI
from app.api_client.base_api_client import BaseAPIClient

app = FastAPI()

client = BaseAPIClient(API_URL, API_KEY)

@app.get('/')
def read_root():
    return {'message': 'Welcome to the API'}
