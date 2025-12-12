import os
import pytest
import httpx

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from ai_observability.app.main import app  # noqa: E402


@pytest.mark.asyncio
async def test_metrics_endpoint():
    transport = httpx.ASGITransport(app=app, lifespan="on")
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/llm/proxy", json={"model": "dummy-llm", "input": "ping"})
        metrics_resp = await client.get("/metrics")
        assert metrics_resp.status_code == 200
        assert "llm_latency_ms" in metrics_resp.text
