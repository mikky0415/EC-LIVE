import os
from typing import Optional
import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/items")
async def get_items(
    visible: Optional[str] = Query(None, description="Filter by visibility"),
    order: Optional[str] = Query(None, description="Order direction"),
    sort: Optional[str] = Query(None, description="Sort field"),
    limit: Optional[int] = Query(None, description="Limit number of results"),
    offset: Optional[int] = Query(None, description="Offset for pagination"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    max_image_no: Optional[int] = Query(None, description="Maximum image number"),
    image_size: Optional[str] = Query(None, description="Image size")
):
    """
    Proxy GET requests to BASE API /1/items endpoint with query parameter passthrough.
    """
    # Read environment variables inside the function for testability
    base_api_url = os.getenv("BASE_API_URL", "https://api.base.ec")
    base_access_token = os.getenv("BASE_ACCESS_TOKEN")
    
    # Check if BASE_ACCESS_TOKEN is configured
    if not base_access_token:
        raise HTTPException(
            status_code=500,
            detail="BASE_ACCESS_TOKEN environment variable is not set"
        )
    
    # Prepare query parameters, excluding None values
    query_params = {}
    if visible is not None:
        query_params["visible"] = visible
    if order is not None:
        query_params["order"] = order
    if sort is not None:
        query_params["sort"] = sort
    if limit is not None:
        query_params["limit"] = limit
    if offset is not None:
        query_params["offset"] = offset
    if category_id is not None:
        query_params["category_id"] = category_id
    if max_image_no is not None:
        query_params["max_image_no"] = max_image_no
    if image_size is not None:
        query_params["image_size"] = image_size
    
    # Prepare headers for BASE API request
    headers = {
        "Authorization": f"Bearer {base_access_token}"
    }
    
    # Make request to BASE API
    try:
        upstream_url = f"{base_api_url.rstrip('/')}/1/items"
        response = requests.get(
            upstream_url,
            headers=headers,
            params=query_params,
            timeout=30  # 30 second timeout
        )
        
        # Try to parse JSON response from upstream
        try:
            response_data = response.json()
        except ValueError:
            # If response is not JSON, return a generic error
            response_data = {
                "error": "Upstream API returned non-JSON response",
                "status_code": response.status_code
            }
        
        # Return response with same status code as upstream
        return JSONResponse(
            content=response_data,
            status_code=response.status_code
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Request to BASE API timed out"
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to BASE API"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with BASE API: {str(e)}"
        )