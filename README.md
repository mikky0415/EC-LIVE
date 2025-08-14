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
- `/healthz` lightweight health check for load balancers
- `/config` GET/POST to view/update runtime API config
- `/api/test` connection test summary
- `/items` Proxy to BASE API `/1/items` (requires env `BASE_ACCESS_TOKEN`)
- `/callback` OAuth2 redirect URI (receives `code`, `state`)
- `/auth/exchange` POST: exchange `code` for tokens (uses env creds)
- `/auth/refresh` POST: refresh access token using `refresh_token` (body or `BASE_REFRESH_TOKEN`)
- `/orders` Proxy to BASE API `/1/orders` (requires env `BASE_ACCESS_TOKEN`)
- `/orders/detail` Proxy to BASE API `/1/orders/detail` (requires env `BASE_ACCESS_TOKEN`)
  
Optional helpers:
- `/auth/authorize` Redirect to BASE authorize URL
- `/auth/debug` Show effective OAuth endpoints and config flags

## Environment variables

- `BASE_API_URL` (default: `https://api.thebase.in`)
- `BASE_ACCESS_TOKEN` (required for `/items`)
- `BASE_CLIENT_ID` (required for `/auth/exchange`)
- `BASE_CLIENT_SECRET` (required for `/auth/exchange`)
- `BASE_OAUTH_TOKEN_URL` (optional, default `https://api.thebase.in/1/oauth/token`)
- `BASE_REDIRECT_URI` (optional, default `https://ec-live.onrender.com/callback`)
- `BASE_REFRESH_TOKEN` (optional, used by `/auth/refresh` if request body omits refresh_token)
- `ITEMS_CACHE_TTL_SECONDS` (optional, default `30`) Cache TTL for successful `/items` responses
- `ITEMS_DEFAULT_BACKOFF_SECONDS` (optional, default `60`) Backoff window when upstream signals rate limiting and no Retry-After is provided
