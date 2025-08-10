from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from app.api_client.base_api_client import BaseAPIClient
from app.config import RuntimeConfig
from app.routers.items import router as items_router
from typing import Optional

app = FastAPI(title="EC-LIVE", version="0.1.0")

# ランタイム設定とクライアント初期化
config = RuntimeConfig()
client = BaseAPIClient(config.api_base_url, config.api_key)

# Routers
app.include_router(items_router)


class APIConfigIn(BaseModel):
    api_base_url: str
    api_key: str


@app.get("/")
def read_root():
    return {"message": "EC-LIVE API running"}


@app.get("/health")
def health():
    test = client.test_connection()
    return {
        "status": "ok",
        "phase": "phase1",
        "version": app.version,
        "config": {
            "api_base_url_set": bool(config.api_base_url),
            "api_key_set": bool(config.api_key),
        },
        "connection": test,
    }


@app.get("/config")
def get_config():
    return {"config": config.masked()}


@app.post("/config")
def set_config(payload: APIConfigIn):
    global config, client
    config.api_base_url = payload.api_base_url.rstrip("/")
    config.api_key = payload.api_key
    client = BaseAPIClient(config.api_base_url, config.api_key)
    return {"config": config.masked()}


@app.get("/api/test")
def api_test():
    return {"result": client.test_connection()}


@app.get("/callback")
def oauth_callback(
    code: Optional[str] = Query(None, description="Authorization code from BASE"),
    state: Optional[str] = Query(None, description="Opaque state value"),
):
    """OAuth2 callback endpoint.
    Receives `code` and optional `state` and returns them for the client to exchange for tokens.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing 'code' query parameter")
    return {"received": True, "code": code, "state": state}