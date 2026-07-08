"""FastAPI entrypoint."""
from __future__ import annotations

import logging
from typing import Dict

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.responses import HTMLResponse
from prometheus_client import generate_latest

from .config import get_settings
from .core.logging import setup_logging
from .llm.dummy_client import DummyLLMClient
from .llm.ollama_client import OllamaLLMClient
from .llm.openai_client import OpenAILLMClient
from .observability import metrics
from .observability.evals import run_evals_for_request
from .observability.logger import log_request
from .observability.privacy import apply_privacy
from .persistence.db import Base, engine
from .persistence.repositories import get_recent_evals, recent_requests, request_counts_by_model
from .core.models import LLMProxyRequest, LLMProxyResponse
from .llm.base import LLMClient


logger = logging.getLogger(__name__)
app = FastAPI(title=get_settings().app_name)
setup_logging()


@app.on_event("startup")
async def startup() -> None:
    """Create database tables on startup."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")


def get_llm_client() -> LLMClient:
    settings = get_settings()
    if settings.llm_provider == "openai":
        return OpenAILLMClient()
    if settings.llm_provider == "ollama":
        return OllamaLLMClient(base_url=settings.ollama_base_url)
    return DummyLLMClient()


@app.post("/llm/proxy", response_model=LLMProxyResponse)
async def llm_proxy(request: LLMProxyRequest, background_tasks: BackgroundTasks, client: LLMClient = Depends(get_llm_client)) -> LLMProxyResponse:
    """Proxy endpoint that wraps LLM calls with observability hooks."""

    settings = get_settings()
    prompt = apply_privacy(request.input)
    logger.info("Processing LLM proxy request for model %s", request.model)
    from time import perf_counter

    start = perf_counter()
    response = await client.generate(model=request.model, prompt=prompt)
    latency_ms = (perf_counter() - start) * 1000

    metrics.REQUEST_COUNT.labels(model=request.model, endpoint="llm_proxy").inc()
    metrics.LATENCY_MS.labels(model=request.model, endpoint="llm_proxy").observe(latency_ms)
    if response.prompt_tokens:
        metrics.TOKENS_TOTAL.labels(model=request.model, kind="prompt").inc(response.prompt_tokens)
    if response.completion_tokens:
        metrics.TOKENS_TOTAL.labels(model=request.model, kind="completion").inc(response.completion_tokens)

    request_id = await log_request(
        model=request.model,
        prompt=request.input,
        response=response.text,
        latency_ms=latency_ms,
        metadata=request.metadata,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
    )

    eval_status = "pending"
    if settings.enable_evals:
        background_tasks.add_task(run_evals_for_request, request_id, request.model, response.text, request.metadata or {})
    else:
        eval_status = "skipped"

    return LLMProxyResponse(model=request.model, latency_ms=latency_ms, output=response.text, eval_status=eval_status)


@app.get("/metrics")
async def metrics_endpoint() -> HTMLResponse:
    """Expose Prometheus metrics."""

    return HTMLResponse(generate_latest())


@app.get("/dashboard")
async def dashboard() -> Dict[str, Dict]:
    """Basic dashboard information as JSON."""

    counts = await request_counts_by_model()
    recent = await recent_requests()
    evals = await get_recent_evals()
    return {
        "requests_by_model": counts,
        "recent_requests": [
            {
                "id": r.id,
                "model": r.model,
                "latency_ms": r.latency_ms,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in recent
        ],
        "recent_evals": [
            {
                "id": e.id,
                "eval_type": e.eval_type,
                "score": e.score,
                "request_id": e.request_id,
                "created_at": e.created_at.isoformat(),
            }
            for e in evals
        ],
    }


@app.get("/evals/{request_id}")
async def evals_for_request(request_id: int):
    """Return evals for a specific request."""

    from .persistence.repositories import get_eval

    records = await get_eval(request_id)
    return [
        {
            "id": r.id,
            "eval_type": r.eval_type,
            "score": r.score,
            "details": r.details,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]


@app.get("/evals/recent")
async def evals_recent():
    """Return recent evaluations."""

    records = await get_recent_evals()
    return [
        {
            "id": r.id,
            "eval_type": r.eval_type,
            "score": r.score,
            "request_id": r.request_id,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]
