"""Data access helpers."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import SessionLocal
from .models import LLMBaseline, LLMEval, LLMRequest


async def create_request(
    *,
    model: str,
    input_text: str,
    output_text: str,
    latency_ms: float,
    prompt_tokens: int | None,
    completion_tokens: int | None,
    metadata: Dict[str, Any],
    session: Optional[AsyncSession] = None,
) -> LLMRequest:
    owns_session = session is None
    session = session or SessionLocal()
    request = LLMRequest(
        model=model,
        input_text=input_text,
        output_text=output_text,
        latency_ms=latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        metadata=metadata,
    )
    session.add(request)
    await session.commit()
    await session.refresh(request)
    if owns_session:
        await session.close()
    return request


async def create_eval(
    *,
    request_id: int,
    eval_type: str,
    score: float,
    details: Dict[str, Any],
    session: Optional[AsyncSession] = None,
) -> LLMEval:
    owns_session = session is None
    session = session or SessionLocal()
    record = LLMEval(request_id=request_id, eval_type=eval_type, score=score, details=details)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    if owns_session:
        await session.close()
    return record


async def get_eval(request_id: int) -> List[LLMEval]:
    async with SessionLocal() as session:
        result = await session.execute(select(LLMEval).where(LLMEval.request_id == request_id))
        return list(result.scalars().all())


async def get_recent_evals(limit: int = 20) -> List[LLMEval]:
    async with SessionLocal() as session:
        result = await session.execute(select(LLMEval).order_by(LLMEval.created_at.desc()).limit(limit))
        return list(result.scalars().all())


async def get_baseline(model: str, use_case: str, input_signature: str) -> Optional[LLMBaseline]:
    async with SessionLocal() as session:
        stmt = select(LLMBaseline).where(
            LLMBaseline.model == model,
            LLMBaseline.use_case == use_case,
            LLMBaseline.input_signature == input_signature,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def seed_baseline(model: str, use_case: str, input_signature: str, expected_output: str, metadata: Dict[str, Any] | None = None) -> LLMBaseline:
    async with SessionLocal() as session:
        baseline = LLMBaseline(
            model=model,
            use_case=use_case,
            input_signature=input_signature,
            expected_output=expected_output,
            metadata=metadata or {},
        )
        session.add(baseline)
        await session.commit()
        await session.refresh(baseline)
        return baseline


async def request_counts_by_model() -> Dict[str, int]:
    async with SessionLocal() as session:
        stmt = select(LLMRequest.model, LLMRequest.id)
        results = await session.execute(stmt)
        counts: Dict[str, int] = {}
        for model, _ in results.all():
            counts[model] = counts.get(model, 0) + 1
        return counts


async def recent_requests(limit: int = 10) -> List[LLMRequest]:
    async with SessionLocal() as session:
        result = await session.execute(select(LLMRequest).order_by(LLMRequest.timestamp.desc()).limit(limit))
        return list(result.scalars().all())
