"""Run evaluations for recent requests."""
from __future__ import annotations

import asyncio

from ai_observability.app.observability.evals import run_evals_for_request
from ai_observability.app.persistence.repositories import recent_requests

ASYNC_LIMIT = 5


async def main() -> None:
    requests = await recent_requests(limit=ASYNC_LIMIT)
    for req in requests:
        await run_evals_for_request(req.id, req.model, req.output_text, req.metadata)


if __name__ == "__main__":
    asyncio.run(main())
