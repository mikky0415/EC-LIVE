# EC-LIVE

## Description
This is the initial implementation of the API connection infrastructure and test suite.

## Requirements
- Python 3.7+
- FastAPI
- Uvicorn
- Requests
- Pydantic

## Running the Application
To run the application, use the following command:

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `/` health message
- `/health` runtime and connection status
- `/config` GET/POST to view/update runtime API config
- `/api/test` connection test summary
- `/items` Proxy to BASE API `/1/items` (requires env `BASE_ACCESS_TOKEN`)

## Environment variables

- `BASE_API_URL` (default: `https://api.base.ec`)
- `BASE_ACCESS_TOKEN` (required for `/items`)
