"""SQLAlchemy models."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    model: Mapped[str] = mapped_column(String(100), index=True)
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[float] = mapped_column(Float)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    evals: Mapped[list["LLMEval"]] = relationship("LLMEval", back_populates="request")


class LLMEval(Base):
    __tablename__ = "llm_evals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("llm_requests.id"), index=True)
    eval_type: Mapped[str] = mapped_column(String(50))
    score: Mapped[float] = mapped_column(Float)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    request: Mapped[LLMRequest] = relationship("LLMRequest", back_populates="evals")


class LLMBaseline(Base):
    __tablename__ = "llm_baselines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model: Mapped[str] = mapped_column(String(100), index=True)
    use_case: Mapped[str] = mapped_column(String(100), index=True)
    input_signature: Mapped[str] = mapped_column(String(256), index=True)
    expected_output: Mapped[str] = mapped_column(Text)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
