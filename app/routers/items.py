import os
import requests
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/items")
async def get_items(
    visible: Optional[str] = Query(None, description="Filter by visibility"),
    order: Optional[str] = Query(None, description="Order field"),
    sort: Optional[str] = Query(None, description="Sort direction"),
    limit: Optional[int] = Query(None, description="Number of items to return"),
    offset: Optional[int] = Query(None, description="Number of items to skip"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    max_image_no: Optional[int] = Query(None, description="Maximum number of images"),
    image_size: Optional[str] = Query(None, description="Image size")
):
    """
    Get items from BASE API /1/items endpoint.
    Proxies request to BASE API with query parameters.
    """
    # Get configuration from environment variables
    base_api_url = os.getenv('BASE_API_URL', 'https://api.base.ec')
    base_access_token = os.getenv('BASE_ACCESS_TOKEN')
    
    # Validate that BASE_ACCESS_TOKEN is provided
    if not base_access_token:
        raise HTTPException(
            status_code=500,
            detail="BASE_ACCESS_TOKEN environment variable is required but not set"
        )
    
    # Build query parameters dictionary, excluding None values
    params = {}
    if visible is not None:
        params['visible'] = visible
    if order is not None:
        params['order'] = order
    if sort is not None:
        params['sort'] = sort
    if limit is not None:
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    if category_id is not None:
        params['category_id'] = category_id
    if max_image_no is not None:
        params['max_image_no'] = max_image_no
    if image_size is not None:
        params['image_size'] = image_size
    
    # Make request to BASE API
    url = f"{base_api_url.rstrip('/')}/1/items"
    headers = {
        'Authorization': f'Bearer {base_access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10  # 10 second timeout
        )
        
        # Return the upstream response
        # If it's an error response, we still return the JSON if possible
        try:
            response_data = response.json()
        except ValueError:
            # If response is not valid JSON, return a generic error
            raise HTTPException(
                status_code=502,
                detail="Upstream API returned invalid response"
            )
        
        # Return the response with the same status code as upstream
        return JSONResponse(
            content=response_data,
            status_code=response.status_code
        )
        
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Upstream API request timed out"
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to upstream API"
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream API error: {str(e)}"
        )