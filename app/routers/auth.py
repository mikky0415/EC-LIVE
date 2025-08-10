from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
import requests

router = APIRouter()


class ExchangeIn(BaseModel):
    code: str
    redirect_uri: Optional[str] = None
    use_basic_auth: bool = True


@router.post("/auth/exchange")
def exchange_token(payload: ExchangeIn):
    """Exchange authorization code for access and refresh tokens.
    Reads client credentials from environment variables:
      - BASE_CLIENT_ID
      - BASE_CLIENT_SECRET
      - BASE_OAUTH_TOKEN_URL (default: https://api.base.ec/1/oauth/token)
      - BASE_REDIRECT_URI (default used when redirect_uri not provided)
    """
    client_id = os.getenv("BASE_CLIENT_ID")
    client_secret = os.getenv("BASE_CLIENT_SECRET")
    token_url = os.getenv("BASE_OAUTH_TOKEN_URL", "https://api.thebase.in/1/oauth/token")
    redirect_uri = payload.redirect_uri or os.getenv("BASE_REDIRECT_URI", "https://ec-live.onrender.com/callback")

    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="BASE_CLIENT_ID/BASE_CLIENT_SECRET is not set")

    data = {
        "grant_type": "authorization_code",
        "code": payload.code,
        "redirect_uri": redirect_uri,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Always include in body per docs; optionally also use Basic auth
    data.update({"client_id": client_id, "client_secret": client_secret})
    auth = (client_id, client_secret) if payload.use_basic_auth else None

    try:
        resp = requests.post(token_url, data=data, headers=headers, auth=auth, timeout=30)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code >= 400:
        detail = resp.json() if "application/json" in content_type else resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json() if "application/json" in content_type else {"raw": resp.text}


@router.get("/auth/debug")
def auth_debug():
    """Return computed OAuth endpoints and key params (secrets masked)."""
    client_id = os.getenv("BASE_CLIENT_ID")
    client_secret = os.getenv("BASE_CLIENT_SECRET")
    redirect_uri = os.getenv("BASE_REDIRECT_URI", "https://ec-live.onrender.com/callback")
    authorize_url = os.getenv("BASE_OAUTH_AUTHORIZE_URL", "https://api.thebase.in/1/oauth/authorize")
    token_url = os.getenv("BASE_OAUTH_TOKEN_URL", "https://api.thebase.in/1/oauth/token")

    return {
        "authorize_url": authorize_url,
        "token_url": token_url,
        "client_id_set": bool(client_id),
        "client_secret_set": bool(client_secret),
        "redirect_uri": redirect_uri,
        "example_authorize": f"{authorize_url}?response_type=code&client_id={client_id or 'MISSING'}&redirect_uri={redirect_uri}&scope=read_items&state=ec-live",
    }


@router.get("/auth/authorize")
def get_authorize(
    scope: str = Query("read_items", description="OAuth scopes, space-delimited"),
    state: Optional[str] = Query("ec-live", description="CSRF protection token"),
):
    """Redirect to BASE OAuth authorize endpoint with proper parameters.
    Respects environment variables:
      - BASE_CLIENT_ID (required)
      - BASE_REDIRECT_URI (default: https://ec-live.onrender.com/callback)
      - BASE_OAUTH_AUTHORIZE_URL (default: https://api.thebase.in/1/oauth/authorize)
    """
    client_id = os.getenv("BASE_CLIENT_ID")
    redirect_uri = os.getenv("BASE_REDIRECT_URI", "https://ec-live.onrender.com/callback")
    authorize_url = os.getenv("BASE_OAUTH_AUTHORIZE_URL", "https://api.thebase.in/1/oauth/authorize")

    if not client_id:
        raise HTTPException(status_code=500, detail="BASE_CLIENT_ID is not set")

    # Build query safely
    from urllib.parse import urlencode

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
    }
    if state is not None:
        params["state"] = state

    url = f"{authorize_url}?{urlencode(params)}"
    return RedirectResponse(url)
