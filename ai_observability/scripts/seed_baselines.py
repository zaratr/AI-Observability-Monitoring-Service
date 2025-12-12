"""Seed baseline records for drift detection."""
from __future__ import annotations

import asyncio

from ai_observability.app.observability.drift import text_signature
from ai_observability.app.persistence.repositories import seed_baseline


async def main() -> None:
    prompt = "Tell me a fun fact about space"
    signature = text_signature(prompt)
    await seed_baseline(
        model="dummy-llm",
        use_case="fun_fact",
        input_signature=signature,
        expected_output="Space is vast and mostly empty.",
        metadata={"note": "Sample baseline"},
    )


if __name__ == "__main__":
    asyncio.run(main())
