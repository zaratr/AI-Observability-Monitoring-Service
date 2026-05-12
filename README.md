# LLM-as-a-Judge Eval & Observability System

## ?? 2026 Architecture Modernization
Traditional observability (latency, token count) is no longer enough for GenAI. This service implements an automated **LLM-as-a-Judge** evaluation pipeline to programmatically grade LLM outputs in production.

### Key Features
1. **Automated Vibe Checks:** Replaces manual QA with a structured LLM evaluator (Gemma).
2. **Strict Rubrics & Scorecards:** Evaluates responses based on context adherence, hallucination detection, and policy compliance, outputting structured JSON scorecards.
3. **Production Proxying:** Intercepts LLM traffic to monitor performance degradation and model drift over time.

## ??? Tech Stack
*   **AI / Eval:** LLM-as-a-Judge, Ollama (Gemma)
*   **Backend:** Python, FastAPI
*   **Observability:** Custom structured logging
