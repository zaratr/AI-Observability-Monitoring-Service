import os
import pytest

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from ai_observability.app.persistence import repositories
from ai_observability.app.persistence.db import Base, engine
from ai_observability.app.observability.drift import check_drift, text_signature


@pytest.mark.asyncio
async def test_drift_detection_threshold():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    prompt = "Hello baseline"
    signature = text_signature(prompt)
    await repositories.seed_baseline("dummy-llm", "test", signature, "Hello baseline response")
    similar = await check_drift("dummy-llm", "test", signature, "Hello baseline response!")
    assert not similar.is_drift
    dissimilar = await check_drift("dummy-llm", "test", signature, "Completely different output")
    assert dissimilar.is_drift
