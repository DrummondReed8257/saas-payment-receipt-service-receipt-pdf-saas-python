import httpx

from receipt_service.infrai_pdf import InfraiPdfClient


def test_generate_uses_envelope_and_retries_rate_limit() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"ok": False, "data": None, "error": {"code": "retry"}, "metadata": {}})
        return httpx.Response(200, json={"ok": True, "data": {"job_id": "job-42"}, "error": None, "metadata": {}})

    client = InfraiPdfClient(
        api_key="test-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        sleeper=lambda _: None,
    )

    assert client.generate_receipt("<p>Paid</p>", "pay-42") == {"job_id": "job-42"}
    assert attempts == 2
