"""Hallucination risk estimation."""
from __future__ import annotations

from collections import Counter
from typing import Dict, Optional

CONFIDENT_PHRASES = {"definitely", "certainly", "always", "guaranteed"}


def heuristic_score(response: str) -> float:
    """Simple heuristic score based on confident phrases."""

    tokens = response.lower().split()
    counts = Counter(tokens)
    confident_hits = sum(counts.get(word, 0) for word in CONFIDENT_PHRASES)
    return min(confident_hits / max(len(tokens), 1), 1.0)


def jaccard_similarity(a: str, b: str) -> float:
    set_a, set_b = set(a.split()), set(b.split())
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union


def reference_score(response: str, reference: str) -> float:
    """Score hallucination risk based on reference overlap."""

    overlap = jaccard_similarity(response, reference)
    base_score = 1 - overlap
    return max(0.0, min(1.0, base_score))


def compute_hallucination_score(response: str, reference_text: Optional[str] = None) -> Dict[str, float]:
    """Compute hallucination score using heuristic or reference mode."""

    if reference_text:
        score = reference_score(response, reference_text)
        mode = "reference"
    else:
        score = heuristic_score(response)
        mode = "heuristic"
    return {"score": score, "mode": mode}
