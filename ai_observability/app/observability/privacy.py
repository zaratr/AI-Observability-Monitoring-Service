"""Privacy helpers for masking and truncation."""
from __future__ import annotations

import re
from typing import Optional

from ..config import get_settings

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def mask_pii(text: str) -> str:
    """Mask simple PII patterns from text."""

    masked = EMAIL_PATTERN.sub("[EMAIL]", text)
    masked = SSN_PATTERN.sub("[SSN]", masked)
    return masked


def truncate(text: str, max_chars: Optional[int] = None) -> str:
    """Truncate text to configured maximum."""

    settings = get_settings()
    limit = max_chars or settings.max_stored_chars_per_field
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def apply_privacy(text: str) -> str:
    """Apply masking and truncation if enabled."""

    settings = get_settings()
    if settings.enable_privacy_masking:
        text = mask_pii(text)
    return truncate(text)
