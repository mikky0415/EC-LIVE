# EC-LIVE

## Description
This is the initial implementation of the API connection infrastructure and test suite with BASE API integration.

## Features
- FastAPI application with health checks and configuration endpoints
- BASE API integration for items retrieval through `/items` endpoint
- Comprehensive error handling and timeout management
- Environment-based configuration for secure API access

## Requirements
- Python 3.7+
- FastAPI
- Uvicorn
- Requests
- Pydantic

## Environment Variables
The following environment variables are required for BASE API integration:

- `BASE_API_URL` - BASE API endpoint URL (default: https://api.base.ec)
- `BASE_ACCESS_TOKEN` - BASE API access token (required for `/items` endpoint)

## API Endpoints

### Core Endpoints
- `GET /` - API status message
- `GET /health` - Health check with configuration status
- `GET /config` - Get current configuration (masked)
- `POST /config` - Update configuration
- `GET /api/test` - Test API connection

### BASE API Integration
- `GET /items` - Retrieve items from BASE API with query parameter support
  - Query parameters: `visible`, `order`, `sort`, `limit`, `offset`, `category_id`, `max_image_no`, `image_size`
  - Requires `BASE_ACCESS_TOKEN` environment variable

## Running the Application
To run the application, use the following command:

```bash
# Set required environment variables
export BASE_API_URL=https://api.base.ec
export BASE_ACCESS_TOKEN=your_base_api_token

# Start the server
uvicorn app.main:app --reload
```

## Deployment
For production deployment (e.g., on Render), ensure that environment variables are properly configured in your deployment environment. See [docs/RENDER_DEPLOY_GUIDE.md](./docs/RENDER_DEPLOY_GUIDE.md) for detailed deployment instructions.
