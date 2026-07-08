"""Real Ollama LLM client.

A concrete LLMClient that calls a local (or remote) Ollama server via its HTTP
API (`/api/generate`). This makes the service's "LLM-as-a-Judge" / LLM-proxy
path actually reach a real model instead of the echo/random stubs.

The Ollama HTTP API is simple: POST /api/generate with {model, prompt, stream:false}
returns JSON {response, model, prompt_eval_count, eval_count}. No SDK dependency
— just httpx, which the service already uses elsewhere.

Select it via settings: `LLM_PROVIDER=ollama`, and optionally point at a non-local
host with `OLLAMA_BASE_URL=http://host:11434`.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from .base import LLMClient, LLMResponse

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


class OllamaLLMClient:
    """LLMClient backed by an Ollama server's HTTP API.

    Constructed lazily — the httpx client is created on first use so importing
    this module never opens a connection. generate() raises on transport errors
    so callers (the eval pipeline) can handle a down server.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 60.0) -> None:
        self._base_url = (base_url or _DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def generate(self, model: str, prompt: str, **kwargs: Any) -> LLMResponse:
        """Call Ollama /api/generate and return an LLMResponse.

        kwargs supports `options` passthrough (temperature, num_predict, etc.)
        and any extra fields the caller wants merged into the request body.
        """
        client = await self._ensure_client()
        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        # Merge caller-supplied options (e.g. temperature) under Ollama's
        # `options` key, and any other kwargs directly onto the body.
        options = kwargs.pop("options", None)
        if options:
            body["options"] = options
        body.update(kwargs)

        logger.debug("ollama generate model=%s prompt_len=%d", model, len(prompt))
        resp = await client.post(f"{self._base_url}/api/generate", json=body)
        resp.raise_for_status()
        data = resp.json()

        return LLMResponse(
            text=data.get("response", "").strip(),
            model=data.get("model", model),
            prompt_tokens=data.get("prompt_eval_count"),
            completion_tokens=data.get("eval_count"),
        )

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
