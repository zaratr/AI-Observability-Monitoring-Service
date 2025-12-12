import os
import pytest
import httpx

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from ai_observability.app.main import app  # noqa: E402
from ai_observability.app.persistence.repositories import request_counts_by_model  # noqa: E402


@pytest.mark.asyncio
async def test_proxy_logs_and_metrics():
    transport = httpx.ASGITransport(app=app, lifespan="on")
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/llm/proxy",
            json={"model": "dummy-llm", "input": "Hello world", "metadata": {"use_case": "test"}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["model"] == "dummy-llm"
        assert "latency_ms" in data
        metrics_resp = await client.get("/metrics")
        assert metrics_resp.status_code == 200
        assert "llm_requests_total" in metrics_resp.text

    counts = await request_counts_by_model()
    assert counts.get("dummy-llm", 0) >= 1
