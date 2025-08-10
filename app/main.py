from fastapi import FastAPI
from app.api_client.base_api_client import BaseAPIClient
from app.config import API_URL, API_KEY

app = FastAPI()

client = BaseAPIClient(API_URL, API_KEY)

@app.get('/')
def read_root():
    return {'message': 'Welcome to the API'}

@app.get('/japanese')
def read_root_japanese():
    return {'message': 'APIへようこそ'}

@app.get('/ai-model')
def get_ai_model_info():
    return {
        'message': '私はChatGPT-5の機能を含む先進的なAIアシスタントです。',
        'ai_model': 'Advanced AI Assistant with ChatGPT-5 capabilities',
        'language_support': ['Japanese', 'English'],
        'response_in_japanese': True
    }
