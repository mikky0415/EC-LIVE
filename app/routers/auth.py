from fastapi import APIRouter, HTTPException
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

    auth = None
    if payload.use_basic_auth:
        auth = (client_id, client_secret)
    else:
        # Include in body if not using Basic auth
        data.update({"client_id": client_id, "client_secret": client_secret})

    try:
        resp = requests.post(token_url, data=data, headers=headers, auth=auth, timeout=15)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

    content_type = resp.headers.get("Content-Type", "")
    if resp.status_code >= 400:
        detail = resp.json() if "application/json" in content_type else resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json() if "application/json" in content_type else {"raw": resp.text}
