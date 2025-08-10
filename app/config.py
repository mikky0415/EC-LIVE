import os
from pydantic import BaseModel


class RuntimeConfig(BaseModel):
    api_base_url: str = os.getenv("EC_API_BASE_URL", "")
    api_key: str = os.getenv("EC_API_KEY", "")

    def masked(self) -> dict:
        return {
            "api_base_url": self.api_base_url,
            "api_key_set": bool(self.api_key),
            "api_key_preview": (self.api_key[:4] + "***" + self.api_key[-2:]) if self.api_key else "",
        }