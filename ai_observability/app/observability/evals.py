"""Evaluation pipeline for LLM requests."""
from __future__ import annotations

from typing import Dict

from ..config import get_settings
from ..observability import hallucination, metrics
from ..persistence import repositories


async def run_evals_for_request(
    request_id: int,
    model: str,
    response_text: str,
    metadata: Dict,
) -> None:
    """Run configured evaluations for a request."""

    settings = get_settings()
    if not settings.enable_evals:
        return

    reference_text = metadata.get("reference_text") if metadata else None
    hallucination_result = hallucination.compute_hallucination_score(response_text, reference_text)
    eval_record = await repositories.create_eval(
        request_id=request_id,
        eval_type="hallucination",
        score=hallucination_result["score"],
        details=hallucination_result,
    )
    metrics.HALLUCINATION_SCORE.labels(model=model, eval_type="hallucination").set(hallucination_result["score"])

    use_case = (metadata or {}).get("use_case", "default")
    input_signature = (metadata or {}).get("input_signature")
    if input_signature:
        from .drift import check_drift

        drift_result = await check_drift(model=model, use_case=use_case, input_signature=input_signature, response_text=response_text)
        await repositories.create_eval(
            request_id=request_id,
            eval_type="drift",
            score=1 - drift_result.similarity,
            details=drift_result.dict(),
        )
        if drift_result.is_drift:
            metrics.DRIFT_ALERTS.labels(model=model, use_case=use_case).inc()
