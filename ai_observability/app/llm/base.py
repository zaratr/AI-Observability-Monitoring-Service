"""LLM client interfaces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""

    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class LLMClient(Protocol):
    """Protocol for LLM clients."""

    async def generate(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """Generate text from the LLM."""
