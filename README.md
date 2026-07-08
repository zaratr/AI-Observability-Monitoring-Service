# LLM-as-a-Judge Eval & Observability System

## 2026 Architecture Modernization
Traditional observability (latency, token count) is no longer enough for GenAI. This service implements an automated **LLM-as-a-Judge** evaluation pipeline to programmatically grade LLM outputs in production.

### Key Features
1. **Automated Vibe Checks:** Replaces manual QA with a structured LLM evaluator (Gemma via Ollama).
2. **Strict Rubrics & Scorecards:** Evaluates responses based on context adherence, hallucination detection, and policy compliance, outputting structured JSON scorecards.
3. **Production Proxying:** Intercepts LLM traffic to monitor performance degradation and model drift over time. The LLM proxy reaches a real model when `LLM_PROVIDER=ollama`.

## Tech Stack
*   **AI / Eval:** LLM-as-a-Judge, Ollama (Gemma) — real HTTP client via the `LLMClient` protocol
*   **Backend:** Python, FastAPI
*   **Observability:** Custom structured logging, Prometheus metrics

## LLM providers

The service selects an LLM backend via the `LLM_PROVIDER` env var:

| Provider | `LLM_PROVIDER` | What it does |
|---|---|---|
| **Ollama** | `ollama` | Calls a local/remote Ollama server (`/api/generate`) — real model inference. Set `OLLAMA_BASE_URL` if not localhost. |
| OpenAI (stub) | `openai` | Echo stub retained for offline dev. |
| Dummy (default) | `dummy` | Random-suffix stub, no network. |

The Ollama client implements the `LLMClient` Protocol (`ai_observability/app/llm/base.py`), so it drops into the existing proxy + eval pipeline without changes to the request path.

## Eval scoring

The eval pipeline (`observability/evals.py`) grades responses on hallucination, drift, and privacy. The hallucination scorer currently uses Jaccard-overlap against an optional reference text (a heuristic baseline). The LLM-as-a-Judge path is available through the `ollama` provider for prompts that benefit from model-based grading.
