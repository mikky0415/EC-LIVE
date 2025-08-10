from typing import Optional, Dict, Any
import requests


class BaseAPIClient:
    """
    Phase1 最小実装:
    - 認証情報の保持
    - 接続テストの提供（設定確認中心、ネットワークは任意）
    """
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: float = 5.0):
        self.base_url = (base_url or "").rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def headers(self) -> Dict[str, str]:
        headers = {"User-Agent": "EC-LIVE/phase1"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def test_connection(self) -> Dict[str, Any]:
        """
        Phase1では「設定が揃っているか」を主判定としつつ、
        base_url が http(s) の場合は軽量に HEAD を試み、失敗しても設定が揃っていれば ok とする。
        """
        if not self.configured:
            return {"configured": False, "ok": False, "reason": "not_configured"}

        ok = True
        reason = "configured"
        if self.base_url.startswith("http"):
            try:
                resp = requests.head(self.base_url, timeout=self.timeout, headers=self.headers())
                ok = resp.status_code < 500
                reason = f"http_status_{resp.status_code}"
            except Exception as e:
                # Phase1はネットワークに依存しない評価を優先
                ok = True
                reason = f"skipped_network_error:{type(e).__name__}"

        return {"configured": True, "ok": ok, "reason": reason}