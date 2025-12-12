"""Stub OpenAI-like client."""
from __future__ import annotations

from typing import Any

from .base import LLMClient, LLMResponse


class OpenAILLMClient:
    """Simplified OpenAI client stub.

    Replace with real OpenAI API calls if desired.
    """

    async def generate(self, model: str, prompt: str, **kwargs: Any) -> LLMResponse:
        text = f"[OpenAI:{model}] Echo: {prompt}"
        return LLMResponse(text=text, model=model, prompt_tokens=len(prompt.split()), completion_tokens=len(text.split()))
