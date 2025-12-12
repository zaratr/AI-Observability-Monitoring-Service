"""Pydantic schemas for API requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LLMProxyRequest(BaseModel):
    """Schema for incoming LLM proxy requests."""

    model: str
    input: str = Field(..., description="Prompt or user message")
    metadata: Optional[Dict[str, Any]] = None


class LLMProxyResponse(BaseModel):
    """Schema for outgoing LLM proxy responses."""

    model: str
    latency_ms: float
    output: str
    eval_status: str


class EvalResult(BaseModel):
    """Schema representing an evaluation result."""

    id: int
    request_id: int
    eval_type: str
    score: float
    details: Dict[str, Any]
    created_at: datetime


class DriftResult(BaseModel):
    """Result of drift detection."""

    is_drift: bool
    similarity: float
    threshold: float
    baseline_id: Optional[int]
