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
):
    """Proxy to BASE API items endpoint.
    Requires BASE_ACCESS_TOKEN set in environment.
    """
    # Read env at request time to support dynamic changes and tests
    base_api_url = os.getenv("BASE_API_URL", "https://api.base.ec")
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
        }.items()
        if v is not None
    }

    try:
        resp = requests.get(
            f"{base_api_url}/1/items",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            timeout=15,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    # Map BASE API response appropriately
    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code >= 400:
        detail = resp.json() if "application/json" in content_type else resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json() if "application/json" in content_type else {"raw": resp.text}
