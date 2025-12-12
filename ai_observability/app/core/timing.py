"""Timing utilities for latency measurement."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def track_latency() -> Iterator[float]:
    """Context manager yielding latency in milliseconds."""

    start = time.perf_counter()
    yield lambda: (time.perf_counter() - start) * 1000
