from fastapi import APIRouter, Query, HTTPException
import os
import requests
from typing import Optional
import time


router = APIRouter()

# Simple in-memory cache to reduce upstream hits
_ORDERS_CACHE: dict[str, dict] = {}
_CACHE_TTL_SECONDS = int(os.getenv("ORDERS_CACHE_TTL_SECONDS", os.getenv("ITEMS_CACHE_TTL_SECONDS", "30")))

# Backoff registry for rate limits (per access token)
_RATE_LIMIT_BACKOFF: dict[str, float] = {}  # token -> until_timestamp
_DEFAULT_BACKOFF_SECONDS = int(os.getenv("ORDERS_DEFAULT_BACKOFF_SECONDS", os.getenv("ITEMS_DEFAULT_BACKOFF_SECONDS", "60")))


def _guard_rate_limit(token: str):
    now = time.time()
    until = _RATE_LIMIT_BACKOFF.get(token)
    if until and now < until:
        retry_after = int(until - now)
        raise HTTPException(status_code=429, detail={"error": "rate_limited", "retry_after": retry_after}, headers={"Retry-After": str(retry_after)})


def _handle_upstream_error(resp: requests.Response, access_token: str):
    content_type = resp.headers.get("Content-Type", "")
    data = None
    if "application/json" in content_type.lower():
        try:
            data = resp.json()
        except ValueError:
            data = None

    if resp.status_code >= 400:
        detail = data if data is not None else (resp.text or f"HTTP {resp.status_code}")
        retry_after = resp.headers.get("Retry-After")
        base_error_code = None
        if isinstance(data, dict):
            base_error_code = str(data.get("error") or "").strip()

        backoff_secs_calc = None
        if base_error_code == "hour_api_limit":
            now = time.time()
            gm = time.gmtime(now)
            sec_past_hour = gm.tm_min * 60 + gm.tm_sec
            backoff_secs_calc = max(5, 3600 - sec_past_hour)
        elif base_error_code == "day_api_limit":
            now = time.time()
            gm = time.gmtime(now)
            sec_past_day = gm.tm_hour * 3600 + gm.tm_min * 60 + gm.tm_sec
            backoff_secs_calc = max(60, 86400 - sec_past_day)

        if resp.status_code == 429 or retry_after or backoff_secs_calc is not None:
            try:
                backoff_secs = int(retry_after) if (retry_after and retry_after.isdigit()) else (backoff_secs_calc if backoff_secs_calc is not None else _DEFAULT_BACKOFF_SECONDS)
            except Exception:
                backoff_secs = _DEFAULT_BACKOFF_SECONDS
            _RATE_LIMIT_BACKOFF[access_token] = time.time() + max(backoff_secs, 1)
            raise HTTPException(status_code=429, detail=detail, headers={"Retry-After": retry_after or str(backoff_secs)})

        raise HTTPException(status_code=resp.status_code, detail=detail)


@router.get("/orders")
def list_orders(
    status: Optional[str] = Query(None, description="Order status filter"),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
):
    """Proxy to BASE API orders endpoint (/1/orders)."""
    base_api_url = os.getenv("BASE_API_URL", "https://api.thebase.in")
    access_token = os.getenv("BASE_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(status_code=500, detail="BASE_ACCESS_TOKEN is not set")

    params = {k: v for k, v in {"status": status, "limit": limit, "offset": offset}.items() if v is not None}

    _guard_rate_limit(access_token)

    # Cache
    now = time.time()
    key_parts = [f"{k}={v}" for k, v in sorted(params.items())]
    cache_key = f"orders|{access_token}|{'&'.join(key_parts)}"
    entry = _ORDERS_CACHE.get(cache_key)
    if entry and (now - entry["ts"]) <= _CACHE_TTL_SECONDS:
        return entry["data"]

    try:
        resp = requests.get(
            f"{base_api_url}/1/orders",
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

    _handle_upstream_error(resp, access_token)

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type.lower():
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text}
    else:
        data = {"raw": resp.text}

    _ORDERS_CACHE[cache_key] = {"ts": now, "data": data}
    return data


@router.get("/orders/detail")
def order_detail(order_id: int = Query(..., ge=1)):
    """Proxy to BASE API orders/detail endpoint."""
    base_api_url = os.getenv("BASE_API_URL", "https://api.thebase.in")
    access_token = os.getenv("BASE_ACCESS_TOKEN")
    if not access_token:
        raise HTTPException(status_code=500, detail="BASE_ACCESS_TOKEN is not set")

    _guard_rate_limit(access_token)

    try:
        resp = requests.get(
            f"{base_api_url}/1/orders/detail",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "User-Agent": "EC-LIVE/1.0 (+https://ec-live.onrender.com)",
            },
            params={"order_id": order_id},
            timeout=15,
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    _handle_upstream_error(resp, access_token)

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" in content_type.lower():
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text}
    else:
        data = {"raw": resp.text}

    return data
