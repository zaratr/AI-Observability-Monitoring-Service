"""Persistence-aware logging helpers."""
from __future__ import annotations

from typing import Any, Dict

from ..persistence import repositories
from .privacy import apply_privacy


async def log_request(
    model: str,
    prompt: str,
    response: str,
    latency_ms: float,
    metadata: Dict[str, Any] | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
) -> int:
    """Persist a request/response pair and return the record id."""

    masked_prompt = apply_privacy(prompt)
    masked_response = apply_privacy(response)
    record = await repositories.create_request(
        model=model,
        input_text=masked_prompt,
        output_text=masked_response,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        metadata=metadata or {},
    )
    return record.id
