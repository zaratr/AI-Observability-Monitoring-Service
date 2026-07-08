"""Tests for the OllamaLLMClient.

Uses an in-process mock of the Ollama /api/generate endpoint so no real server
is required. Verifies:
  - the client maps the Ollama JSON response to LLMResponse correctly
  - request body shape is correct (model, prompt, stream:false)
  - HTTP errors propagate so callers can handle a down server
  - the client satisfies the LLMClient Protocol (duck-typed)
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Make the app package importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _make_fake_post(response_json: dict, raise_for_status_exc=None):
    """Build a fake async post() coroutine returning a mock response."""
    fake_resp = MagicMock()
    fake_resp.json.return_value = response_json
    if raise_for_status_exc:
        fake_resp.raise_for_status.side_effect = raise_for_status_exc
    else:
        fake_resp.raise_for_status = MagicMock()  # no-op
    return AsyncMock(return_value=fake_resp)


@pytest.mark.asyncio
async def test_ollama_generate_maps_response():
    """A successful /api/generate call returns an LLMResponse with the right fields."""
    from ai_observability.app.llm.ollama_client import OllamaLLMClient

    client = OllamaLLMClient(base_url="http://fake:11434")
    fake_post = _make_fake_post({
        "response": " Paris is the capital of France.",
        "model": "gemma:2b",
        "prompt_eval_count": 12,
        "eval_count": 8,
    })

    fake_http = MagicMock()
    fake_http.post = fake_post
    with patch.object(client, "_ensure_client", new=AsyncMock(return_value=fake_http)):
        result = await client.generate(model="gemma:2b", prompt="What is the capital of France?")

    assert result.text == "Paris is the capital of France."  # stripped
    assert result.model == "gemma:2b"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 8


@pytest.mark.asyncio
async def test_ollama_generate_sends_correct_body():
    """The request body must include model, prompt, stream:false, and options."""
    from ai_observability.app.llm.ollama_client import OllamaLLMClient

    client = OllamaLLMClient(base_url="http://fake:11434")
    fake_post = _make_fake_post({"response": "ok", "model": "m", "prompt_eval_count": 0, "eval_count": 0})

    fake_http = MagicMock()
    fake_http.post = fake_post
    with patch.object(client, "_ensure_client", new=AsyncMock(return_value=fake_http)):
        await client.generate(model="gemma:2b", prompt="hi", options={"temperature": 0.0})

    fake_post.assert_called_once()
    call_args = fake_post.call_args
    assert call_args.args[0] == "http://fake:11434/api/generate"
    body = call_args.kwargs["json"]
    assert body["model"] == "gemma:2b"
    assert body["prompt"] == "hi"
    assert body["stream"] is False
    assert body["options"] == {"temperature": 0.0}


@pytest.mark.asyncio
async def test_ollama_generate_raises_on_http_error():
    """A transport/HTTP error must propagate so callers can handle a down server."""
    from ai_observability.app.llm.ollama_client import OllamaLLMClient
    import httpx

    client = OllamaLLMClient(base_url="http://fake:11434")
    exc = httpx.HTTPStatusError(
        "server error",
        request=httpx.Request("POST", "http://fake"),
        response=httpx.Response(500),
    )
    fake_post = _make_fake_post({}, raise_for_status_exc=exc)

    fake_http = MagicMock()
    fake_http.post = fake_post
    with patch.object(client, "_ensure_client", new=AsyncMock(return_value=fake_http)):
        with pytest.raises(httpx.HTTPStatusError):
            await client.generate(model="m", prompt="p")


def test_ollama_client_satisfies_protocol():
    """OllamaLLMClient duck-types as an LLMClient (has an async generate())."""
    from ai_observability.app.llm.ollama_client import OllamaLLMClient
    from ai_observability.app.llm.base import LLMClient

    client = OllamaLLMClient()
    # The Protocol is structural; just confirm generate is an awaitable method.
    assert hasattr(client, "generate")
    assert asyncio.iscoroutinefunction(client.generate)


def test_factory_returns_ollama_when_configured():
    """When settings.llm_provider == 'ollama', the factory builds an OllamaLLMClient.

    Tested by replicating the factory logic (avoids importing main.py, which
    pulls in the async DB engine and other deps unnecessary for this unit test).
    """
    from ai_observability.app.llm.ollama_client import OllamaLLMClient
    from ai_observability.app.llm.dummy_client import DummyLLMClient
    from ai_observability.app.llm.openai_client import OpenAILLMClient

    def factory(provider: str, base_url: str = "http://localhost:11434"):
        # Mirrors get_llm_client() in main.py.
        if provider == "openai":
            return OpenAILLMClient()
        if provider == "ollama":
            return OllamaLLMClient(base_url=base_url)
        return DummyLLMClient()

    assert isinstance(factory("ollama"), OllamaLLMClient)
    assert isinstance(factory("openai"), OpenAILLMClient)
    assert isinstance(factory("dummy"), DummyLLMClient)
    assert isinstance(factory("anything-else"), DummyLLMClient)  # default fallback
