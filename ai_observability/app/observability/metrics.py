"""Prometheus metrics definitions."""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total LLM requests",
    labelnames=("model", "endpoint"),
)

LATENCY_MS = Histogram(
    "llm_latency_ms",
    "LLM request latency in milliseconds",
    buckets=(50, 100, 200, 400, 800, 1600, 3200),
    labelnames=("model", "endpoint"),
)

TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Total tokens observed",
    labelnames=("model", "kind"),
)

HALLUCINATION_SCORE = Gauge(
    "llm_hallucination_score",
    "Latest hallucination score",
    labelnames=("model", "eval_type"),
)

DRIFT_ALERTS = Counter(
    "llm_drift_alerts_total",
    "Total drift alerts",
    labelnames=("model", "use_case"),
)
