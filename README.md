# AI Observability & Monitoring Service

This service acts as an observability and monitoring layer for LLM-based applications. It proxies requests, logs behavior, tracks latency, monitors hallucination risk, and detects potential model drift over time.

## Features
- FastAPI-based proxy endpoint that wraps LLM calls and records latency, throughput, and token usage.
- Prometheus metrics via `/metrics`.
- Basic dashboard JSON via `/dashboard` summarizing recent requests and evals.
- Privacy controls for masking emails/SSNs and truncating stored text.
- Hallucination risk scoring (heuristic and reference-based) and drift detection based on baselines.
- SQLite/PostgreSQL-ready persistence using SQLAlchemy.
- Dummy and stub OpenAI LLM clients.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the API locally:
   ```bash
   uvicorn ai_observability.app.main:app --reload
   ```
3. Or use Docker:
   ```bash
   docker-compose up --build
   ```

## Usage
- Send requests to `/llm/proxy` with a JSON body:
  ```json
  {
    "model": "dummy-llm",
    "input": "Tell me a fun fact",
    "metadata": {"user_id": "123", "use_case": "fun_fact"}
  }
  ```
- Access Prometheus metrics at `/metrics`.
- View dashboard data at `/dashboard`.
- Retrieve evals via `/evals/{request_id}` or `/evals/recent`.

## Hallucination Scoring
- Heuristic mode counts confident phrases to estimate risk (0-1).
- Reference mode computes Jaccard overlap with provided `reference_text` metadata; lower overlap increases risk.

## Drift Detection
- Baselines are stored per model/use-case/signature.
- New responses compare length-based similarity to baselines and flag drift if similarity falls below the configured threshold.
- Use `ai_observability/scripts/seed_baselines.py` to seed example baselines.

## Why Observability Matters
Proactive monitoring of LLM behavior helps surface regressions, slowdowns, and hallucination risks before they impact end-users. This service provides a simple starting point for production readiness.
