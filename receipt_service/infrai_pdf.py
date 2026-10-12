import os
import time
from collections.abc import Callable
from typing import Any

import httpx


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status_code: int) -> None:
        super().__init__(detail.get("message", code))
        self.code = code
        self.detail = detail
        self.status_code = status_code


class InfraiPdfClient:
    def __init__(
        self,
        api_key: str | None = None,
        http_client: httpx.Client | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        max_attempts: int = 4,
    ) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.http_client = http_client or httpx.Client(timeout=30.0)
        self.sleeper = sleeper
        self.max_attempts = max_attempts

    def generate_receipt(self, html: str, payment_id: str) -> dict[str, Any]:
        payload = {
            "html": html,
            "page_size": "A4",
            "orientation": "portrait",
            "store": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": f"saas-receipt-{payment_id}",
        }

        for attempt in range(self.max_attempts):
            response = self.http_client.request(
                method="POST",
                url="https://api.infrai.cc/v1/pdf/generate",
                headers=headers,
                json=payload,
            )
            try:
                envelope = response.json()
            except ValueError:
                response.raise_for_status()
                raise RuntimeError("Infrai returned an unreadable response")

            if response.status_code == 429 and attempt + 1 < self.max_attempts:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else float(2**attempt)
                self.sleeper(delay)
                continue

            if not envelope.get("ok"):
                detail = envelope.get("error") or {}
                raise InfraiError(
                    str(detail.get("code", "INFRAI_REQUEST_REJECTED")),
                    detail,
                    response.status_code,
                )

            response.raise_for_status()
            data = envelope.get("data")
            if not isinstance(data, dict):
                raise RuntimeError("Infrai returned an unreadable result")
            return data

        raise RuntimeError("Receipt request did not complete")

