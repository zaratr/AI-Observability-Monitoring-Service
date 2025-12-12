"""Dummy LLM client for local testing."""
from __future__ import annotations

import random
from typing import Any

from .base import LLMClient, LLMResponse


class DummyLLMClient:
    """LLM client returning deterministic yet varied responses."""

    async def generate(self, model: str, prompt: str, **kwargs: Any) -> LLMResponse:
        suffixes = [
            "This is a safe and concise answer.",
            "Based on the available information, here's a summary.",
            "I recommend verifying this with trusted sources.",
        ]
        text = f"Response to: {prompt}\n{random.choice(suffixes)}"
        return LLMResponse(text=text, model=model, prompt_tokens=len(prompt.split()), completion_tokens=12)
