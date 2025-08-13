from fastapi import APIRouter, Query, HTTPException
import os
import requests
from typing import Optional
import time


router = APIRouter()

# Simple in-memory cache to reduce upstream hits
_ITEMS_CACHE: dict[str, dict] = {}
_CACHE_TTL_SECONDS = int(os.getenv("ITEMS_CACHE_TTL_SECONDS", "30"))

# Backoff registry for rate limits (per access token)
_RATE_LIMIT_BACKOFF: dict[str, float] = {}  # token -> until_timestamp
_DEFAULT_BACKOFF_SECONDS = int(os.getenv("ITEMS_DEFAULT_BACKOFF_SECONDS", "60"))


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

    # Global backoff check (avoid hitting upstream during Retry-After window)
    now = time.time()
    until = _RATE_LIMIT_BACKOFF.get(access_token)
    if until and now < until:
        retry_after = int(until - now)
        raise HTTPException(status_code=429, detail={"error": "rate_limited", "retry_after": retry_after}, headers={"Retry-After": str(retry_after)})

    # Cache lookup (only for successful prior responses)
    key_parts = [f"{k}={v}" for k, v in sorted(params.items())]
    cache_key = f"{access_token}|{'&'.join(key_parts)}"
    entry = _ITEMS_CACHE.get(cache_key)
    if entry and (now - entry["ts"]) <= _CACHE_TTL_SECONDS:
        return entry["data"]

    try:
        resp = requests.get(
            f"{base_api_url}/1/items",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "User-Agent": "EC-LIVE/1.0 (+https://ec-live.onrender.com)",
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
        # Propagate rate limit specifics when available
        retry_after = resp.headers.get("Retry-After")
        # Map BASE specific error codes for rate limit (they may return 400)
        base_error_code = None
        if isinstance(data, dict):
            base_error_code = str(data.get("error") or "").strip()

        # Compute conservative backoff windows
        backoff_secs_calc = None
        if base_error_code == "hour_api_limit":
            # Wait until next hour (UTC-based). 00分でリセット。
            now = time.time()
            gm = time.gmtime(now)
            sec_past_hour = gm.tm_min * 60 + gm.tm_sec
            backoff_secs_calc = max(5, 3600 - sec_past_hour)
        elif base_error_code == "day_api_limit":
            # Wait until next day (UTC-based). 00:00でリセット。
            now = time.time()
            gm = time.gmtime(now)
            sec_past_day = gm.tm_hour * 3600 + gm.tm_min * 60 + gm.tm_sec
            backoff_secs_calc = max(60, 86400 - sec_past_day)

        # Handle rate limit and raise
        if resp.status_code == 429 or retry_after or backoff_secs_calc is not None:
            # Record backoff window
            try:
                backoff_secs = int(retry_after) if (retry_after and retry_after.isdigit()) else (backoff_secs_calc if backoff_secs_calc is not None else _DEFAULT_BACKOFF_SECONDS)
            except Exception:
                backoff_secs = _DEFAULT_BACKOFF_SECONDS
            _RATE_LIMIT_BACKOFF[access_token] = time.time() + max(backoff_secs, 1)
            raise HTTPException(status_code=429, detail=detail, headers={"Retry-After": retry_after or str(backoff_secs)})

        raise HTTPException(status_code=resp.status_code, detail=detail)

    result = data if data is not None else {"raw": resp.text}

    # Store successful response in cache
    try:
        _ITEMS_CACHE[cache_key] = {"ts": now, "data": result}
    except Exception:
        pass

    return result
