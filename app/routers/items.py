from fastapi import APIRouter, Query, HTTPException
import os
import requests
from typing import Optional


router = APIRouter()


@router.get("/items")
def list_items(
    visible: Optional[int] = Query(None, ge=0, le=1),
    order: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
    category_id: Optional[int] = Query(None, ge=1),
    max_image_no: Optional[int] = Query(None, ge=1, le=20),
    image_size: Optional[str] = Query(None, description="origin,76,146,300,500,640,sp_480,sp_640 (comma-separated)"),
):
    """Proxy to BASE API items endpoint.
    Requires BASE_ACCESS_TOKEN set in environment.
    """
    # Read env at request time to support dynamic changes and tests
    base_api_url = os.getenv("BASE_API_URL", "https://api.thebase.in")
    access_token = os.getenv("BASE_ACCESS_TOKEN")

    if not access_token:
        raise HTTPException(status_code=500, detail="BASE_ACCESS_TOKEN is not set")

    params = {
        k: v
        for k, v in {
            "visible": visible,
            "order": order,
            "sort": sort,
            "limit": limit,
            "offset": offset,
            "category_id": category_id,
            "max_image_no": max_image_no,
            "image_size": image_size,
        }.items()
        if v is not None
    }

    try:
        resp = requests.get(
            f"{base_api_url}/1/items",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            params=params,
            timeout=15,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    # Map BASE API response appropriately (robust to non-JSON bodies)
    content_type = resp.headers.get("Content-Type", "")
    data = None
    if "application/json" in content_type.lower():
        try:
            data = resp.json()
        except ValueError:
            data = None

    if resp.status_code >= 400:
        detail = data if data is not None else (resp.text or f"HTTP {resp.status_code}")
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return data if data is not None else {"raw": resp.text}
