# EC-LIVE

## Description
This is the initial implementation of the API connection infrastructure and test suite.

## Production URL

- Render (production): https://ec-live.onrender.com/

## OAuth2 Callback URL

- https://ec-live.onrender.com/callback

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
- `/callback` OAuth2 redirect URI (receives `code`, `state`)
- `/auth/exchange` POST: exchange `code` for tokens (uses env creds)

## Environment variables

- `BASE_API_URL` (default: `https://api.base.ec`)
- `BASE_ACCESS_TOKEN` (required for `/items`)
- `BASE_CLIENT_ID` (required for `/auth/exchange`)
- `BASE_CLIENT_SECRET` (required for `/auth/exchange`)
- `BASE_OAUTH_TOKEN_URL` (optional, default `https://api.base.ec/1/oauth/token`)
- `BASE_REDIRECT_URI` (optional, default `https://ec-live.onrender.com/callback`)
