"""Model drift detection logic."""
from __future__ import annotations

import hashlib
from typing import Optional

from ..config import get_settings
from ..core.models import DriftResult
from ..persistence import repositories


def text_signature(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def similarity_by_length(a: str, b: str) -> float:
    """Approximate similarity using normalized length difference."""

    if not a and not b:
        return 1.0
    max_len = max(len(a), len(b), 1)
    return 1 - abs(len(a) - len(b)) / max_len


async def check_drift(model: str, use_case: str, input_signature: str, response_text: str) -> DriftResult:
    """Compare response to stored baseline and flag drift."""

    settings = get_settings()
    baseline = await repositories.get_baseline(model, use_case, input_signature)
    similarity = 1.0
    baseline_id: Optional[int] = None
    if baseline:
        similarity = similarity_by_length(response_text, baseline.expected_output)
        baseline_id = baseline.id
    is_drift = similarity < settings.drift_threshold
    return DriftResult(is_drift=is_drift, similarity=similarity, threshold=settings.drift_threshold, baseline_id=baseline_id)
