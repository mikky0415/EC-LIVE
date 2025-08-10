# EC-LIVE

## Description
This is a FastAPI application that provides an API proxy to BASE API services with connection infrastructure and test suite.

## Requirements
- Python 3.7+
- FastAPI
- Uvicorn
- Requests
- Pydantic

## Environment Variables
- `BASE_API_URL` (optional): BASE API endpoint URL (default: https://api.base.ec)
- `BASE_ACCESS_TOKEN` (required): Access token for BASE API authentication

## API Endpoints
- `GET /` - Root endpoint with API status message
- `GET /health` - Health check endpoint
- `GET /config` - Get current configuration (masked)
- `POST /config` - Set API configuration  
- `GET /api/test` - Test API connection
- `GET /items` - Proxy to BASE API items endpoint with query parameter support

## Running the Application
To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

For production deployment, ensure `BASE_ACCESS_TOKEN` is set in your environment.
